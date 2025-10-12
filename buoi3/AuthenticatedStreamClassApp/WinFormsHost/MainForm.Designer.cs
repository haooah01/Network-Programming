namespace WinFormsHost
{
    partial class MainForm
    {
        /// <summary>
        ///  Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        ///  Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        ///  Required method for Designer support - do not modify
        ///  the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            startButton = new Button();
            requireClientCertCheckBox = new CheckBox();
            outputTextBox = new TextBox();
            progressBar = new ProgressBar();
            SuspendLayout();
            // 
            // startButton
            // 
            startButton.Anchor = AnchorStyles.Top | AnchorStyles.Right;
            startButton.Location = new Point(497, 12);
            startButton.Name = "startButton";
            startButton.Size = new Size(116, 29);
            startButton.TabIndex = 0;
            startButton.Text = "Start Demo";
            startButton.UseVisualStyleBackColor = true;
            startButton.Click += startButton_Click;
            // 
            // requireClientCertCheckBox
            // 
            requireClientCertCheckBox.AutoSize = true;
            requireClientCertCheckBox.Location = new Point(12, 16);
            requireClientCertCheckBox.Name = "requireClientCertCheckBox";
            requireClientCertCheckBox.Size = new Size(224, 24);
            requireClientCertCheckBox.TabIndex = 1;
            requireClientCertCheckBox.Text = "Require client certificate demo";
            requireClientCertCheckBox.UseVisualStyleBackColor = true;
            // 
            // outputTextBox
            // 
            outputTextBox.Anchor = AnchorStyles.Top | AnchorStyles.Bottom | AnchorStyles.Left | AnchorStyles.Right;
            outputTextBox.Location = new Point(12, 56);
            outputTextBox.Multiline = true;
            outputTextBox.Name = "outputTextBox";
            outputTextBox.ReadOnly = true;
            outputTextBox.ScrollBars = ScrollBars.Vertical;
            outputTextBox.Size = new Size(601, 311);
            outputTextBox.TabIndex = 2;
            // 
            // progressBar
            // 
            progressBar.Anchor = AnchorStyles.Bottom | AnchorStyles.Left | AnchorStyles.Right;
            progressBar.Location = new Point(12, 383);
            progressBar.MarqueeAnimationSpeed = 30;
            progressBar.Name = "progressBar";
            progressBar.Size = new Size(601, 23);
            progressBar.Style = ProgressBarStyle.Blocks;
            progressBar.TabIndex = 3;
            // 
            // MainForm
            // 
            AutoScaleDimensions = new SizeF(8F, 20F);
            AutoScaleMode = AutoScaleMode.Font;
            ClientSize = new Size(625, 418);
            Controls.Add(progressBar);
            Controls.Add(outputTextBox);
            Controls.Add(requireClientCertCheckBox);
            Controls.Add(startButton);
            MinimumSize = new Size(480, 320);
            Name = "MainForm";
            Text = "Authenticated Stream Demo";
            ResumeLayout(false);
            PerformLayout();
        }

        #endregion

        private Button startButton;
        private CheckBox requireClientCertCheckBox;
        private TextBox outputTextBox;
        private ProgressBar progressBar;
    }
}
