using System;
using System.Linq;
using System.IO;
using System.Security.Cryptography;
using System.Windows.Forms;
using KeePass.DataExchange;
using KeePass.Forms;
using KeePass.Plugins;
using KeePassLib.Utility;
using KeePass;
using KeePassLib.Serialization;
using KeePass.App;
using KeePassLib.Keys;
using KeePassLib;

namespace AxiomKeepass
{
    public sealed class AxiomKeepassExt : Plugin
    {
        private IPluginHost m_host = null;
	private static readonly byte[] Key = {
		0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
		0x09, 0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16,
		0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
		0x09, 0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16
    	};
	private static readonly byte[] IV = {
        	0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
        	0x09, 0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16
    	};

        public override bool Initialize(IPluginHost host)
        {
            if (host == null) return false;
            m_host = host;
            m_host.MainWindow.FileOpened += this.OnFileOpened;
            return true;
        }

        private void OnFileOpened(object sender, FileOpenedEventArgs e)
        {
            var database = m_host.Database;
	    var keydata = m_host.Database.MasterKey.UserKeys.ElementAt(0).KeyData;
            var rootGroup = database.RootGroup;
            string exportFilePath = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), "axiomvault");
            string exportFilePath_enc = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), "axiomvault.enc");
            bool bResult = false;
            bool bExistedAlready = true;

            PwExportInfo pwExportInfo = new PwExportInfo(rootGroup, database);
            FileFormatProvider ffp = Program.FileFormatPool.Find("KeePass XML (2.x)");
            IOConnectionInfo ioc = IOConnectionInfo.FromPath(exportFilePath);

            try
            {
		Stream s = IOConnection.OpenWrite(ioc);
                bExistedAlready = IOConnection.FileExists(ioc);
                try {
			bResult = ffp.Export(pwExportInfo, s, null);
			using (Aes aes = Aes.Create())
			{
				byte[] key = Key;
				byte[] iv = IV;

				using (FileStream inputStream = new FileStream(exportFilePath, FileMode.Open))
				using (FileStream outputStream = new FileStream(exportFilePath_enc, FileMode.Create))
				using (CryptoStream cryptoStream = new CryptoStream(
					outputStream,
					aes.CreateEncryptor(key, iv),
					CryptoStreamMode.Write
				)) {
					inputStream.CopyTo(cryptoStream);
				}
			}
			File.Delete(exportFilePath);
		}

                finally { if (s != null) s.Close(); }

            }
            catch (Exception ex) { MessageService.ShowWarning(ex); }

            if (bResult && !bExistedAlready)
            {
                try { IOConnection.DeleteFile(ioc); }
                catch (Exception) { }
            }
        }
    }
}

