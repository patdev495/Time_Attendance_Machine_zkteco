using System;
using System.IO;
using System.Reflection;
using System.Reflection.Emit;

public class HwDevCommandDumper
{
    public static void Main()
    {
        string clientPath = @"C:\Program Files (x86)\Hanvon\FaceAtt\Client";
        
        AppDomain.CurrentDomain.AssemblyResolve += (sender, args) => {
            string name = new AssemblyName(args.Name).Name;
            string depPath = Path.Combine(clientPath, name + ".dll");
            if (File.Exists(depPath)) {
                try { return Assembly.LoadFile(depPath); } catch {}
            }
            return null;
        };

        string path = Path.Combine(clientPath, "HwDevOp.dll");
        Assembly asm = Assembly.LoadFile(path);
        Type type = asm.GetType("Hanvon.FaceID.HwDevOp");
        if (type == null)
        {
            Console.WriteLine("Type Hanvon.FaceID.HwDevOp not found in HwDevOp.dll");
            return;
        }

        MethodInfo method = type.GetMethod("HwDevCommand", BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static | BindingFlags.Instance);
        if (method == null)
        {
            Console.WriteLine("Method HwDevCommand not found");
            return;
        }

        Console.WriteLine("=== Disassembling Hanvon.FaceID.HwDevOp.HwDevCommand ===");
        DumpMethod(method);
    }

    private static void DumpMethod(MethodInfo method)
    {
        MethodBody body = method.GetMethodBody();
        if (body == null)
        {
            Console.WriteLine("No method body (might be extern / PInvoke)");
            return;
        }

        byte[] il = body.GetILAsByteArray();
        int pos = 0;
        while (pos < il.Length)
        {
            int offset = pos;
            byte opByte = il[pos++];
            OpCode op = OpCodes.Nop;
            if (opByte == 0xFE)
            {
                if (pos >= il.Length) break;
                byte opByte2 = il[pos++];
                foreach (FieldInfo fi in typeof(OpCodes).GetFields(BindingFlags.Public | BindingFlags.Static))
                {
                    OpCode o = (OpCode)fi.GetValue(null);
                    if (o.Value == ((0xFE << 8) | opByte2))
                    {
                        op = o;
                        break;
                    }
                }
            }
            else
            {
                foreach (FieldInfo fi in typeof(OpCodes).GetFields(BindingFlags.Public | BindingFlags.Static))
                {
                    OpCode o = (OpCode)fi.GetValue(null);
                    if (o.Value == opByte)
                    {
                        op = o;
                        break;
                    }
                }
            }

            string operand = "";
            switch (op.OperandType)
            {
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
