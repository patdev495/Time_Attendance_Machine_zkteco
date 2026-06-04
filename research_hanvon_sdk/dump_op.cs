using System;
using System.Reflection;

public class OpDumper
{
    public static void Main()
    {
        string hwDevOpPath = @"C:\Program Files (x86)\Hanvon\FaceAtt\Client\HwDevOp.dll";
        Assembly asm = Assembly.LoadFile(hwDevOpPath);
        Type type = asm.GetType("Hanvon.FaceID.HWDeviceOperation.DeviceOperation");
        if (type == null)
        {
            Console.WriteLine("Type Hanvon.FaceID.HWDeviceOperation.DeviceOperation not found in HwDevOp.dll");
            // Let's search for similar names
            foreach (Type t in asm.GetTypes())
            {
                if (t.Name.Contains("DeviceOperation") || t.FullName.Contains("DeviceOperation"))
                {
                    Console.WriteLine("Found similar type: " + t.FullName);
                }
            }
            return;
        }

        Console.WriteLine("Found type: " + type.FullName);
        foreach (MethodInfo method in type.GetMethods(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance | BindingFlags.Static))
        {
            if (method.DeclaringType == type)
            {
                Console.WriteLine("\nMethod: " + method.ReturnType.Name + " " + method.Name);
                foreach (ParameterInfo p in method.GetParameters())
                {
                    Console.WriteLine("  Param: " + p.ParameterType.Name + " " + p.Name);
                }
            }
        }
    }
}
