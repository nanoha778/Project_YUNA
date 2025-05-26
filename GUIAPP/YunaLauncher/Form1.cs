using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace YunaLauncher
{

    public partial class Form1 : Form
    {
        Process pythonLoopProcess;
        private bool isAutoOnceEnabled = false;

        private bool isShuttingDown = false;

        public Form1()
        {

            InitializeComponent();
            this.Icon = Properties.Resources.AppIcon;  // ← Resources に追加した名前

        }

        private void Form1_Load(object sender, EventArgs e)
        {
            StartPythonHost();  // 起動時にバックエンド起動

            richTextBox1.Font = new Font("Segoe UI Emoji", 10);
            richTextBox2.Font = new Font("Segoe UI Emoji", 10);


            AppendLog(richTextBox1, "読込中...");
            StartLoopHost();    // 自動ループ用 command_host.py 起動
            button2.Text = "🔴 自動実行 OFF";
            button2.BackColor = Color.LightGray;
            if (File.Exists(envPath))
            {
                var lines = File.ReadAllLines(envPath);
                foreach (var line in lines)
                {
                    if (line.StartsWith("OPENAI_API_KEY="))
                    {
                        textBoxOpenAI.Text = line.Substring("OPENAI_API_KEY=".Length);
                        textBoxOpenAI.UseSystemPasswordChar = true;
                    }
                    if (line.StartsWith("GEMINI_API_KEY="))
                    {
                        textBoxGemini.Text = line.Substring("GEMINI_API_KEY=".Length);
                        textBoxGemini.UseSystemPasswordChar = true;
                    }
                }
            }
        }

        private void button1_Click(object sender, EventArgs e)
        {
            string input = textBox1.Text.Trim();
            if (!string.IsNullOrWhiteSpace(input))
            {
                SendTalkCommand(input);
            }
        }
        private void richTextBox1_KeyDown(object sender, KeyEventArgs e)
        {
            if (e.KeyCode == Keys.Enter)
            {
                e.SuppressKeyPress = true; // Enterキーの改行を抑制（任意）

                // 最後の改行前の文字列を取得
                string[] lines = richTextBox1.Lines;

                if (lines.Length > 0)
                {
                    string input = lines[lines.Length - 1].Trim();

                    if (!string.IsNullOrWhiteSpace(input))
                    {
                        AppendLog(richTextBox1, "\n");
                        SendTalkCommand(input);
                    }
                }
            }
        }

        private void button2_Click(object sender, EventArgs e)
        {
            isAutoOnceEnabled = !isAutoOnceEnabled;

            if (isAutoOnceEnabled)
            {
                button2.Text = "🟢 自動実行 ON";
                button2.BackColor = Color.LightGreen;
                AppendLog(richTextBox2, "✅ 自動 /once 実行が有効になりました\n");
                if (pythonLoopProcess != null && !pythonLoopProcess.HasExited)
                {
                    pythonLoopProcess.StandardInput.WriteLine("/once");
                    pythonLoopProcess.StandardInput.Flush();
                    AppendLog(richTextBox2, "▶ トグルON → /once 初回実行\n");
                }
            }
            else
            {
                button2.Text = "🔴 自動実行 OFF";
                button2.BackColor = Color.LightGray;
                AppendLog(richTextBox2, "🛑 自動 /once 実行が無効になりました\n");
            }
        }

        private void textBox1_TextChanged(object sender, EventArgs e)
        {

        }

        Process pythonProcess;

        private void StartPythonHost()
        {
            var baseDir = Application.StartupPath;
            var scriptPath = Path.Combine(baseDir, "python", "command_host.py");

            var psi = new ProcessStartInfo
            {
                FileName = "python",
                Arguments = $"\"{scriptPath}\"",
                WorkingDirectory = Path.GetDirectoryName(scriptPath),
                UseShellExecute = false,
                RedirectStandardInput = true,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                StandardOutputEncoding = Encoding.UTF8,
                StandardErrorEncoding = Encoding.UTF8,
                CreateNoWindow = true
            };



            pythonProcess = new Process { StartInfo = psi };
            pythonProcess.Start();

            // 応答受信用の別スレッド
            Task.Run(() =>
            {
                while (!pythonProcess.StandardOutput.EndOfStream)
                {
                    string line = pythonProcess.StandardOutput.ReadLine();

                    // 特定の文言を検出！
                    if (line.Contains("コマンド (/talk"))
                    {
                        Invoke((MethodInvoker)(() =>
                        {
                            AppendLog(richTextBox1, "✅ Python準備完了！" + Environment.NewLine);
                            panel1.Hide();
                            // ロード画面OFF
                        }));
                    }
                    else
                    {
                        // ログ出力など
                        Invoke((MethodInvoker)(() =>
                        {
                            AppendLog(richTextBox1, line + Environment.NewLine);
                        }));
                    }
                }
            });


        }
        private void UpdateEnvVariable(string key, string value)
        {
            var lines = File.Exists(envPath) ? File.ReadAllLines(envPath).ToList() : new List<string>();
            bool found = false;

            for (int i = 0; i < lines.Count; i++)
            {
                if (lines[i].StartsWith(key + "="))
                {
                    lines[i] = key + "=" + value;
                    found = true;
                    break;
                }
            }

            if (!found)
                lines.Add(key + "=" + value);

            File.WriteAllLines(envPath, lines, Encoding.UTF8);
        }


        private void StartLoopHost()
        {
            var baseDir = Application.StartupPath;
            var scriptPath = Path.Combine(baseDir, "python", "command_host.py");

            var psiLoop = new ProcessStartInfo
            {
                FileName = "python",
                Arguments = $"\"{scriptPath}\"",
                WorkingDirectory = Path.GetDirectoryName(scriptPath),
                UseShellExecute = false,
                RedirectStandardInput = true,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                StandardOutputEncoding = Encoding.UTF8,
                StandardErrorEncoding = Encoding.UTF8,
                CreateNoWindow = true
            };


            pythonLoopProcess = new Process { StartInfo = psiLoop };
            pythonLoopProcess.Start();
            Task.Run(() =>
            {
                while (!pythonLoopProcess.StandardOutput.EndOfStream)
                {
                    string line = pythonLoopProcess.StandardOutput.ReadLine();

                    Invoke((MethodInvoker)(() =>
                    {
                        AppendLog(richTextBox2, "[LOOP] " + line, isError: false);

                        if (!isShuttingDown && isAutoOnceEnabled && line.Contains("コマンド (/talk"))
                        {
                            pythonLoopProcess.StandardInput.WriteLine("/once");
                            pythonLoopProcess.StandardInput.Flush();
                            AppendLog(richTextBox2, "▶ /once を送信しました\n");
                        }
                    }));
                }
            });


        }
        private void AppendLog(RichTextBox richTextBox, string text, bool isError = false)
        {
            richTextBox.SelectionColor = isError ? Color.Red : Color.Black;
            richTextBox.AppendText(text + Environment.NewLine);
            richTextBox.SelectionColor = Color.Black; // 戻しておく
        }


        private void SendTalkCommand(string message)
        {
            if (pythonProcess == null || pythonProcess.HasExited)
            {
                MessageBox.Show("Pythonプロセスが起動していません！");
                return;
            }

            pythonProcess.StandardInput.WriteLine($"/talk {message}");
            pythonProcess.StandardInput.Flush();
        }
       


        private void AppendOutput(string line)
        {
            if (!string.IsNullOrWhiteSpace(line))
                AppendLog(richTextBox1, line + Environment.NewLine);  // TextBoxに出力表示
        }


        protected override void OnFormClosing(FormClosingEventArgs e)
        {
            isShuttingDown = true;
            TerminateProcess(pythonProcess);
            TerminateProcess(pythonLoopProcess);
            base.OnFormClosing(e);
        }

        private void TerminateProcess(Process proc)
        {
            try
            {
                if (proc != null && !proc.HasExited)
                {
                    proc.StandardInput.WriteLine("/exit");
                    proc.StandardInput.Flush();
                    if (!proc.WaitForExit(3000))
                    {
                        proc.Kill(); // 応答がないときは強制終了
                    }
                    proc.Dispose();
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"プロセス終了中にエラー: {ex.Message}");
            }
        }



        private void panel1_Paint(object sender, PaintEventArgs e)
        {

        }

        private string envPath => Path.Combine(Application.StartupPath, ".env");

        private void textBoxOpenAI_KeyDown(object sender, KeyEventArgs e)
        {
            if (e.KeyCode == Keys.Enter)
            {
                UpdateEnvVariable("OPENAI_API_KEY", textBoxOpenAI.Text.Trim());
                textBoxOpenAI.UseSystemPasswordChar = true;
                e.SuppressKeyPress = true; // ビープ音抑制
            }
        }


        private void textBoxGemini_KeyDown(object sender, KeyEventArgs e)
        {
            if (e.KeyCode == Keys.Enter)
            {
                UpdateEnvVariable("GEMINI_API_KEY", textBoxGemini.Text.Trim());
                textBoxGemini.UseSystemPasswordChar = true;
                e.SuppressKeyPress = true; // ビープ音抑制
            }
        }

        private void textBoxOpenAI_Click(object sender, EventArgs e)
        {
            textBoxOpenAI.UseSystemPasswordChar = false;
        }

        private void textBoxGemini_Click(object sender, EventArgs e)
        {
            textBoxGemini.UseSystemPasswordChar = false;
        }

        private void labelLogMain_Click(object sender, EventArgs e)
        {

        }
    }
}
