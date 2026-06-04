using System;
using System.IO;
using System.Reflection;

public class BusinessDumper
{
    public static void Main()
    {
        AppDomain.CurrentDomain.AssemblyResolve += (sender, args) => {
            string name = new AssemblyName(args.Name).Name + ".dll";
            string depPath = Path.Combine(@"C:\Program Files (x86)\Hanvon\FaceAtt\Client", name);
            if (File.Exists(depPath))
            {
                try { return Assembly.LoadFile(depPath); } catch {}
            }
            return null;
        };

        string path = @"C:\Program Files (x86)\Hanvon\FaceAtt\Client\KMS.Common.dll";
        Assembly asm = Assembly.LoadFile(path);
        
        try {
            var types = asm.GetTypes();
            Console.WriteLine("Total Types Succeeded: " + types.Length);
            foreach (var t in types) {
                if (t != null) {
                    Console.WriteLine("Type: " + t.FullName);
                }
            }
        }
        catch (ReflectionTypeLoadException rtle) {
            Console.WriteLine("RTLE caught. Types count: " + rtle.Types.Length);
            foreach (var t in rtle.Types) {
                if (t != null) {
                    Console.WriteLine("RTLE Type: " + t.FullName);
                }
            }
        }
    }
}
