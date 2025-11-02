using System;
using System.Drawing;
using System.Windows.Forms;

namespace NetProject
{
    public partial class MainForm : Form
    {
        private Button btnSayHello = null!;
        private Label lblMessage = null!;
        private TextBox txtName = null!;
        private Label lblName = null!;

        public MainForm()
        {
            InitializeComponent();
        }

        private void InitializeComponent()
        {
            // Form settings
            this.Text = "Hello World App";
            this.Size = new Size(400, 300);
            this.StartPosition = FormStartPosition.CenterScreen;

            // Name label
            lblName = new Label();
            lblName.Text = "Enter your name:";
            lblName.Location = new Point(20, 20);
            lblName.Size = new Size(100, 23);

            // Name text box
            txtName = new TextBox();
            txtName.Location = new Point(130, 20);
            txtName.Size = new Size(200, 23);

            // Say Hello button
            btnSayHello = new Button();
            btnSayHello.Text = "Say Hello";
            btnSayHello.Location = new Point(20, 60);
            btnSayHello.Size = new Size(100, 30);
            btnSayHello.Click += BtnSayHello_Click;

            // Message label
            lblMessage = new Label();
            lblMessage.Text = "";
            lblMessage.Location = new Point(20, 110);
            lblMessage.Size = new Size(350, 50);
            lblMessage.Font = new Font("Arial", 12, FontStyle.Bold);
            lblMessage.ForeColor = Color.Blue;

            // Add controls to form
            this.Controls.Add(lblName);
            this.Controls.Add(txtName);
            this.Controls.Add(btnSayHello);
            this.Controls.Add(lblMessage);
        }

        private void BtnSayHello_Click(object? sender, EventArgs e)
        {
            string name = txtName.Text.Trim();
            if (string.IsNullOrEmpty(name))
            {
                lblMessage.Text = "Hello, World!";
            }
            else
            {
                lblMessage.Text = $"Hello, {name}!";
            }
        }
    }
}