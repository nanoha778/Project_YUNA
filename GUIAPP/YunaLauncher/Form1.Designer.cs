namespace YunaLauncher
{
    partial class Form1
    {
        private System.ComponentModel.IContainer components = null;

        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
                labelLoading.Dispose();
                progressBarLoading.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows フォーム デザイナーで生成されたコード

        private void InitializeComponent()
        {
            this.components = new System.ComponentModel.Container();
            this.textBox1 = new System.Windows.Forms.TextBox();
            this.richTextBox1 = new System.Windows.Forms.RichTextBox();
            this.panel1 = new System.Windows.Forms.Panel();
            this.labelLoading = new System.Windows.Forms.Label();
            this.progressBarLoading = new System.Windows.Forms.ProgressBar();
            this.contextMenuStrip1 = new System.Windows.Forms.ContextMenuStrip(this.components);
            this.richTextBox2 = new System.Windows.Forms.RichTextBox();
            this.button2 = new System.Windows.Forms.Button();
            this.textBoxOpenAI = new System.Windows.Forms.TextBox();
            this.textBoxGemini = new System.Windows.Forms.TextBox();
            this.labelOpenAI = new System.Windows.Forms.Label();
            this.labelGemini = new System.Windows.Forms.Label();
            this.labelLogMain = new System.Windows.Forms.Label();
            this.labelLogLoop = new System.Windows.Forms.Label();
            this.panel1.SuspendLayout();
            this.SuspendLayout();
            // 
            // textBox1
            // 
            this.textBox1.Font = new System.Drawing.Font("MS UI Gothic", 16F);
            this.textBox1.Location = new System.Drawing.Point(34, 622);
            this.textBox1.Name = "textBox1";
            this.textBox1.Size = new System.Drawing.Size(723, 34);
            this.textBox1.TabIndex = 1;
            this.textBox1.TextChanged += new System.EventHandler(this.textBox1_TextChanged);
            // 
            // richTextBox1
            // 
            this.richTextBox1.BackColor = System.Drawing.SystemColors.Info;
            this.richTextBox1.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.richTextBox1.Font = new System.Drawing.Font("Consolas", 10F);
            this.richTextBox1.ForeColor = System.Drawing.SystemColors.InfoText;
            this.richTextBox1.Location = new System.Drawing.Point(25, 47);
            this.richTextBox1.Name = "richTextBox1";
            this.richTextBox1.Size = new System.Drawing.Size(732, 768);
            this.richTextBox1.TabIndex = 2;
            this.richTextBox1.Text = "";
            this.richTextBox1.KeyDown += new System.Windows.Forms.KeyEventHandler(this.richTextBox1_KeyDown);
            // 
            // panel1
            // 
            this.panel1.BackColor = System.Drawing.Color.DarkSlateGray;
            this.panel1.Controls.Add(this.labelLoading);
            this.panel1.Controls.Add(this.progressBarLoading);
            this.panel1.Location = new System.Drawing.Point(0, 0);
            this.panel1.Name = "panel1";
            this.panel1.Size = new System.Drawing.Size(1570, 847);
            this.panel1.TabIndex = 3;
            // 
            // labelLoading
            // 
            this.labelLoading.Font = new System.Drawing.Font("Segoe UI", 18F, System.Drawing.FontStyle.Bold);
            this.labelLoading.ForeColor = System.Drawing.Color.White;
            this.labelLoading.Location = new System.Drawing.Point(585, 300);
            this.labelLoading.Name = "labelLoading";
            this.labelLoading.Size = new System.Drawing.Size(400, 50);
            this.labelLoading.TabIndex = 0;
            this.labelLoading.Text = "🔄 起動中... しばらくお待ちください";
            this.labelLoading.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // progressBarLoading
            // 
            this.progressBarLoading.Location = new System.Drawing.Point(585, 360);
            this.progressBarLoading.Name = "progressBarLoading";
            this.progressBarLoading.Size = new System.Drawing.Size(400, 30);
            this.progressBarLoading.Style = System.Windows.Forms.ProgressBarStyle.Marquee;
            this.progressBarLoading.TabIndex = 1;
            // 
            // contextMenuStrip1
            // 
            this.contextMenuStrip1.ImageScalingSize = new System.Drawing.Size(20, 20);
            this.contextMenuStrip1.Name = "contextMenuStrip1";
            this.contextMenuStrip1.Size = new System.Drawing.Size(61, 4);
            // 
            // richTextBox2
            // 
            this.richTextBox2.BackColor = System.Drawing.SystemColors.Info;
            this.richTextBox2.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.richTextBox2.Font = new System.Drawing.Font("Consolas", 10F);
            this.richTextBox2.ForeColor = System.Drawing.SystemColors.InfoText;
            this.richTextBox2.Location = new System.Drawing.Point(802, 47);
            this.richTextBox2.Name = "richTextBox2";
            this.richTextBox2.ReadOnly = true;
            this.richTextBox2.Size = new System.Drawing.Size(745, 610);
            this.richTextBox2.TabIndex = 4;
            this.richTextBox2.Text = "";
            // 
            // button2
            // 
            this.button2.Font = new System.Drawing.Font("Segoe UI Emoji", 20F);
            this.button2.Location = new System.Drawing.Point(1090, 670);
            this.button2.Name = "button2";
            this.button2.Size = new System.Drawing.Size(320, 60);
            this.button2.TabIndex = 5;
            this.button2.Text = "自動実行";
            this.button2.UseVisualStyleBackColor = true;
            this.button2.Click += new System.EventHandler(this.button2_Click);
            // 
            // textBoxOpenAI
            // 
            this.textBoxOpenAI.Font = new System.Drawing.Font("MS UI Gothic", 12F);
            this.textBoxOpenAI.Location = new System.Drawing.Point(859, 735);
            this.textBoxOpenAI.Name = "textBoxOpenAI";
            this.textBoxOpenAI.Size = new System.Drawing.Size(654, 27);
            this.textBoxOpenAI.TabIndex = 6;
            this.textBoxOpenAI.UseSystemPasswordChar = true;
            this.textBoxOpenAI.Click += new System.EventHandler(this.textBoxOpenAI_Click);
            this.textBoxOpenAI.KeyDown += new System.Windows.Forms.KeyEventHandler(this.textBoxOpenAI_KeyDown);
            // 
            // textBoxGemini
            // 
            this.textBoxGemini.Font = new System.Drawing.Font("MS UI Gothic", 12F);
            this.textBoxGemini.Location = new System.Drawing.Point(859, 768);
            this.textBoxGemini.Name = "textBoxGemini";
            this.textBoxGemini.Size = new System.Drawing.Size(654, 27);
            this.textBoxGemini.TabIndex = 7;
            this.textBoxGemini.UseSystemPasswordChar = true;
            this.textBoxGemini.Click += new System.EventHandler(this.textBoxGemini_Click);
            this.textBoxGemini.KeyDown += new System.Windows.Forms.KeyEventHandler(this.textBoxGemini_KeyDown);
            // 
            // labelOpenAI
            // 
            this.labelOpenAI.AutoSize = true;
            this.labelOpenAI.Location = new System.Drawing.Point(796, 740);
            this.labelOpenAI.Name = "labelOpenAI";
            this.labelOpenAI.Size = new System.Drawing.Size(57, 15);
            this.labelOpenAI.TabIndex = 8;
            this.labelOpenAI.Text = "OpenAI:";
            // 
            // labelGemini
            // 
            this.labelGemini.AutoSize = true;
            this.labelGemini.Location = new System.Drawing.Point(796, 773);
            this.labelGemini.Name = "labelGemini";
            this.labelGemini.Size = new System.Drawing.Size(53, 15);
            this.labelGemini.TabIndex = 9;
            this.labelGemini.Text = "Gemini:";
            // 
            // labelLogMain
            // 
            this.labelLogMain.AutoSize = true;
            this.labelLogMain.Font = new System.Drawing.Font("MS UI Gothic", 12F, System.Drawing.FontStyle.Bold);
            this.labelLogMain.Location = new System.Drawing.Point(25, 20);
            this.labelLogMain.Name = "labelLogMain";
            this.labelLogMain.Size = new System.Drawing.Size(154, 20);
            this.labelLogMain.TabIndex = 10;
            this.labelLogMain.Text = "▶ メインコンソール";
            this.labelLogMain.Click += new System.EventHandler(this.labelLogMain_Click);
            // 
            // labelLogLoop
            // 
            this.labelLogLoop.AutoSize = true;
            this.labelLogLoop.Font = new System.Drawing.Font("MS UI Gothic", 12F, System.Drawing.FontStyle.Bold);
            this.labelLogLoop.Location = new System.Drawing.Point(802, 20);
            this.labelLogLoop.Name = "labelLogLoop";
            this.labelLogLoop.Size = new System.Drawing.Size(108, 20);
            this.labelLogLoop.TabIndex = 11;
            this.labelLogLoop.Text = "▶ ループログ";
            // 
            // Form1
            // 
            this.BackColor = System.Drawing.Color.FromArgb(((int)(((byte)(245)))), ((int)(((byte)(248)))), ((int)(((byte)(250)))));
            this.ClientSize = new System.Drawing.Size(1570, 843);
            this.Controls.Add(this.panel1);
            this.Controls.Add(this.labelLogLoop);
            this.Controls.Add(this.labelLogMain);
            this.Controls.Add(this.labelGemini);
            this.Controls.Add(this.labelOpenAI);
            this.Controls.Add(this.textBoxGemini);
            this.Controls.Add(this.textBoxOpenAI);
            this.Controls.Add(this.button2);
            this.Controls.Add(this.richTextBox2);
            this.Controls.Add(this.richTextBox1);
            this.Controls.Add(this.textBox1);
            this.Name = "Form1";
            this.Text = "ProjectYUNA Launcher";
            this.Load += new System.EventHandler(this.Form1_Load);
            this.panel1.ResumeLayout(false);
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion
        private System.Windows.Forms.TextBox textBox1;
        private System.Windows.Forms.RichTextBox richTextBox1;
        private System.Windows.Forms.Panel panel1;
        private System.Windows.Forms.ContextMenuStrip contextMenuStrip1;
        private System.Windows.Forms.RichTextBox richTextBox2;
        private System.Windows.Forms.Button button2;
        private System.Windows.Forms.TextBox textBoxOpenAI;
        private System.Windows.Forms.TextBox textBoxGemini;
        private System.Windows.Forms.Label labelOpenAI;
        private System.Windows.Forms.Label labelGemini;
        private System.Windows.Forms.Label labelLogMain;
        private System.Windows.Forms.Label labelLogLoop;
        private System.Windows.Forms.Label labelLoading;
        private System.Windows.Forms.ProgressBar progressBarLoading;
    }
}
