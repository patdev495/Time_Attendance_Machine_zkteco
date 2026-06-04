using System;
using System.IO;
using System.Reflection;

public class BusinessDumper
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
            string exePath = Path.Combine(clientPath, name + ".exe");
            if (File.Exists(exePath)) {
                try { return Assembly.LoadFile(exePath); } catch {}
            }
            return null;
        };

        // Preload DLLs and EXEs
        foreach (string file in Directory.GetFiles(clientPath, "*.dll")) {
            try { Assembly.LoadFile(file); } catch {}
        }
        foreach (string file in Directory.GetFiles(clientPath, "*.exe")) {
            try { Assembly.LoadFile(file); } catch {}
        }

        string path = Path.Combine(clientPath, "KMS.Common.dll");
        Assembly asm = Assembly.LoadFile(path);
        
        try {
            var types = asm.GetTypes();
            Console.WriteLine("Total Types Succeeded: " + types.Length);
            foreach (var t in types) {
                if (t != null && t.FullName != null && t.FullName.StartsWith("Hanvon")) {
                    Console.WriteLine("Hanvon Type: " + t.FullName);
                }
            }
        }
        catch (ReflectionTypeLoadException rtle) {
            Console.WriteLine("RTLE caught. Types count: " + rtle.Types.Length);
            foreach (var t in rtle.Types) {
                if (t != null && t.FullName != null && t.FullName.StartsWith("Hanvon")) {
                    Console.WriteLine("RTLE Hanvon Type: " + t.FullName);
                }
            }
        }
    }
}
