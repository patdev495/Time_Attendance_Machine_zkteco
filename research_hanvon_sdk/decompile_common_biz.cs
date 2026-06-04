using System;
using System.IO;
using System.Reflection;
using System.Reflection.Emit;

public class BusinessDumper
{
    public static void Main()
    {
        string clientPath = @"C:\Program Files (x86)\Hanvon\FaceAtt\Client";
        
        // Setup assembly resolver
        AppDomain.CurrentDomain.AssemblyResolve += (sender, args) => {
            string name = new AssemblyName(args.Name).Name;
            string depPath = Path.Combine(clientPath, name + ".dll");
            if (File.Exists(depPath)) {
                try { return Assembly.LoadFile(depPath); } catch {}
            }
            string exePath = Path.Combine(clientPath, name + ".exe");
            if (File.Exists(exePath)) {
                try { return Assembly.LoadFile(exePath); } catch {}
            }
            return null;
        };

        // Preload all DLLs and EXEs in the Client folder
        foreach (string file in Directory.GetFiles(clientPath, "*.dll")) {
            try { Assembly.LoadFile(file); } catch {}
        }
        foreach (string file in Directory.GetFiles(clientPath, "*.exe")) {
            try { Assembly.LoadFile(file); } catch {}
        }

        Console.WriteLine("=== Trace Assemblies in C# ===");
        Type type = null;
        foreach (var asm in AppDomain.CurrentDomain.GetAssemblies()) {
            Type[] types = null;
            try {
                types = asm.GetTypes();
            }
            catch (ReflectionTypeLoadException rtle) {
                Console.WriteLine("[RTLE] on " + asm.FullName + " - loader exceptions count: " + rtle.LoaderExceptions.Length);
                foreach (var le in rtle.LoaderExceptions) {
                    Console.WriteLine("  le: " + le.Message);
                }
                types = rtle.Types;
            }
            catch (Exception ex) {
                Console.WriteLine("  Error loading types for " + asm.FullName + ": " + ex.GetType().Name + " - " + ex.Message);
                continue;
            }

            if (types == null) {
                Console.WriteLine("  Types list null for " + asm.FullName);
                continue;
            }

            foreach (var t in types) {
                if (t != null && t.FullName != null && t.FullName.IndexOf("BDeviceRelated", StringComparison.OrdinalIgnoreCase) >= 0) {
                    Console.WriteLine("Found matching type: " + t.FullName);
                    Console.WriteLine("  Assembly: " + asm.FullName);
                    Console.WriteLine("  Location: " + asm.Location);
                    if (t.FullName == "Hanvon.KMS.Business.BDeviceRelated") {
                        type = t;
                    }
                }
            }
        }

        if (type == null) {
            Console.WriteLine("FAILED: Type Hanvon.KMS.Business.BDeviceRelated could not be resolved.");
            return;
        }

        string[] methodsToDump = { "DownRcdAndSave", "AutoSyncRcd", "AutoDownRcdAndSave", "ClearRcd" };
        
        foreach (string mName in methodsToDump)
        {
            MethodInfo method = type.GetMethod(mName, BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static | BindingFlags.Instance);
            if (method != null)
            {
                Console.WriteLine("\n=== Disassembling " + type.FullName + "." + method.Name + " ===");
                foreach (ParameterInfo p in method.GetParameters()) {
                    Console.WriteLine("  Param: " + p.ParameterType.Name + " " + p.Name);
                }
                DumpMethod(method);
            }
            else
            {
                Console.WriteLine("Method " + mName + " not found");
            }
        }
    }

    private static void DumpMethod(MethodInfo method)
    {
        MethodBody body = method.GetMethodBody();
        if (body == null) {
            Console.WriteLine("No method body");
            return;
        }

        byte[] il = body.GetILAsByteArray();
        int pos = 0;
        while (pos < il.Length) {
            int offset = pos;
            byte opByte = il[pos++];
            OpCode op = OpCodes.Nop;
            if (opByte == 0xFE) {
                if (pos >= il.Length) break;
                byte opByte2 = il[pos++];
                foreach (FieldInfo fi in typeof(OpCodes).GetFields(BindingFlags.Public | BindingFlags.Static)) {
                    OpCode o = (OpCode)fi.GetValue(null);
                    if (o.Value == ((0xFE << 8) | opByte2)) {
                        op = o;
                        break;
                    }
                }
            }
            else {
                foreach (FieldInfo fi in typeof(OpCodes).GetFields(BindingFlags.Public | BindingFlags.Static)) {
                    OpCode o = (OpCode)fi.GetValue(null);
                    if (o.Value == opByte) {
                        op = o;
                        break;
                    }
                }
            }

            string operand = "";
            switch (op.OperandType) {
                case OperandType.InlineNone:
                    break;
                case OperandType.ShortInlineI:
                case OperandType.ShortInlineVar:
                    operand = il[pos++].ToString("X2");
                    break;
                case OperandType.InlineVar:
                    operand = BitConverter.ToUInt16(il, pos).ToString("X4");
                    pos += 2;
                    break;
                case OperandType.InlineI:
                case OperandType.ShortInlineR:
                    operand = BitConverter.ToInt32(il, pos).ToString("X8");
                    pos += 4;
                    break;
                case OperandType.InlineI8:
                case OperandType.InlineR:
                    operand = BitConverter.ToInt64(il, pos).ToString("X16");
                    pos += 8;
                    break;
                case OperandType.InlineBrTarget:
                    operand = "offset " + (offset + 5 + BitConverter.ToInt32(il, pos)).ToString("X4");
                    pos += 4;
                    break;
                case OperandType.ShortInlineBrTarget:
                    operand = "offset " + (offset + 2 + (sbyte)il[pos++]).ToString("X4");
                    break;
                case OperandType.InlineField:
                case OperandType.InlineMethod:
                case OperandType.InlineTok:
                case OperandType.InlineType:
                    int token = BitConverter.ToInt32(il, pos);
                    operand = "token " + token.ToString("X8");
                    try {
                        MemberInfo member = method.Module.ResolveMember(token);
                        operand += " (" + member.Name + ")";
                    } catch {}
                    pos += 4;
                    break;
                case OperandType.InlineString:
                    int strToken = BitConverter.ToInt32(il, pos);
                    operand = "string token " + strToken.ToString("X8");
                    try {
                        operand += " (" + method.Module.ResolveString(strToken) + ")";
                    } catch {}
                    pos += 4;
                    break;
                default:
                    break;
            }

            Console.WriteLine(string.Format("  IL_{0:X4}: {1,-10} {2}", offset, op.Name, operand));
        }
    }
}
