using System;
using System.IO;
using System.Reflection;

public class StringLister
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

        string path = Path.Combine(clientPath, "FaceId.dll");
        Assembly asm = Assembly.LoadFile(path);
        
        Console.WriteLine("=== Strings in FaceId.dll ===");
        foreach (Type t in asm.GetTypes()) {
            if (t == null) continue;
            foreach (FieldInfo f in t.GetFields(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static)) {
                if (f.FieldType == typeof(string) && f.IsStatic) {
                    try {
                        string val = f.GetValue(null) as string;
                        if (val != null && (val.Contains("GetRecord") || val.Contains("Record") || val.Contains("PARAM"))) {
                            Console.WriteLine("  " + t.FullName + "." + f.Name + " = " + val);
                        }
                    } catch {}
                }
            }
        }
    }
}
