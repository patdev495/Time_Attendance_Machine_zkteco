using System;
using System.IO;
using System.Reflection;

public class SerializerTester
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

        // Preload Newtonsoft.Json
        Assembly.LoadFile(Path.Combine(clientPath, "Newtonsoft.Json.dll"));
        Assembly asm = Assembly.LoadFile(Path.Combine(clientPath, "KMS.Common.dll"));

        Type cmdType = asm.GetType("Hanvon.FaceID.ClientGetRecordCmd");
        object cmd = Activator.CreateInstance(cmdType);
        
        // Set RETURN = "GetRequest"
        cmdType.GetField("RETURN").SetValue(cmd, "GetRequest");

        Type parType = asm.GetType("Hanvon.FaceID.ClientGetRecordCmdPar");
        object param = Activator.CreateInstance(parType);
        
        // Set command = "GetRecord", start_time, end_time
        parType.GetField("command").SetValue(param, "GetRecord");
        parType.GetField("start_time").SetValue(param, "2026-06-04 00:00:00");
        parType.GetField("end_time").SetValue(param, "2026-06-04 23:59:59");
        
        // Assign PARAM field in cmd
        cmdType.GetField("PARAM").SetValue(cmd, param);

        // Serialize using Newtonsoft.Json.JsonConvert.SerializeObject
        Type jsonConvertType = Type.GetType("Newtonsoft.Json.JsonConvert, Newtonsoft.Json");
        if (jsonConvertType == null) {
            // Load by assembly
            Assembly jsonAsm = Assembly.LoadFile(Path.Combine(clientPath, "Newtonsoft.Json.dll"));
            jsonConvertType = jsonAsm.GetType("Newtonsoft.Json.JsonConvert");
        }

        MethodInfo serializeMethod = jsonConvertType.GetMethod("SerializeObject", new Type[] { typeof(object) });
        string json = (string)serializeMethod.Invoke(null, new object[] { cmd });
        
        Console.WriteLine("Serialized JSON:");
        Console.WriteLine(json);
    }
}
