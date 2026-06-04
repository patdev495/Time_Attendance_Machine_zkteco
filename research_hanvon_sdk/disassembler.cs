using System;
using System.Reflection;
using System.Reflection.Emit;
using System.Text;
using System.IO;

public class Disassembler
{
    public static void Main()
    {
        string faceIdPath = @"C:\Program Files (x86)\Hanvon\FaceAtt\Client\FaceId.dll";
        Assembly asm = Assembly.LoadFile(faceIdPath);
        Type type = asm.GetType("Com.FirstSolver.Splash.Xor64Codec");

        Console.WriteLine("=== Disassembling Xor64Codec ===");
        DumpMethod(type.GetMethod("Encode", BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance));
        DumpMethod(type.GetMethod("Decode", BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance));
        DumpMethod(type.GetMethod("set_SecretKey", BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance));
    }

    private static void DumpMethod(MethodInfo method)
    {
        if (method == null)
        {
            Console.WriteLine("Method not found");
            return;
        }

        Console.WriteLine("\nMethod: " + method.Name);
        MethodBody body = method.GetMethodBody();
        if (body == null)
        {
            Console.WriteLine("No method body");
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
                // find double byte opcode
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
