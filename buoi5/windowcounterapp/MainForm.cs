using System;
using System.Diagnostics;
using System.Drawing;
using System.Linq;
using System.Windows.Forms;

namespace WindowCounterApp
{
    public class MainForm : Form
    {
        private Label lblTitle;
        private Button btnCountWindows;
        private Label lblResult;
        private ListBox lstWindows;

        public MainForm()
        {
            this.Text = "Window Counter App";
            this.Size = new Size(500, 400);
            this.StartPosition = FormStartPosition.CenterScreen;
            this.FormBorderStyle = FormBorderStyle.FixedDialog;
            this.MaximizeBox = false;

            lblTitle = new Label
            {
                Text = "Đếm số cửa sổ đang mở trên máy tính",
                Font = new Font("Segoe UI", 14, FontStyle.Bold),
                Dock = DockStyle.Top,
                Height = 40,
                TextAlign = ContentAlignment.MiddleCenter
            };

            btnCountWindows = new Button
            {
                Text = "Đếm cửa sổ",
                Font = new Font("Segoe UI", 12),
                Dock = DockStyle.Top,
                Height = 40
            };
            btnCountWindows.Click += BtnCountWindows_Click;

            lblResult = new Label
            {
                Text = "Số cửa sổ: ...",
                Font = new Font("Segoe UI", 12),
                Dock = DockStyle.Top,
                Height = 30,
                TextAlign = ContentAlignment.MiddleLeft
            };

            lstWindows = new ListBox
            {
                Dock = DockStyle.Fill,
                Font = new Font("Segoe UI", 10)
            };

            var panel = new TableLayoutPanel
            {
                Dock = DockStyle.Fill,
                RowCount = 4,
                ColumnCount = 1
            };
            panel.RowStyles.Add(new RowStyle(SizeType.Absolute, 40));
            panel.RowStyles.Add(new RowStyle(SizeType.Absolute, 40));
            panel.RowStyles.Add(new RowStyle(SizeType.Absolute, 30));
            panel.RowStyles.Add(new RowStyle(SizeType.Percent, 100));
            panel.Controls.Add(lblTitle, 0, 0);
            panel.Controls.Add(btnCountWindows, 0, 1);
            panel.Controls.Add(lblResult, 0, 2);
            panel.Controls.Add(lstWindows, 0, 3);

            this.Controls.Add(panel);
        }

        private void BtnCountWindows_Click(object sender, EventArgs e)
        {
            lstWindows.Items.Clear();
            var windows = Process.GetProcesses()
                .Where(p => !string.IsNullOrEmpty(p.MainWindowTitle))
                .Select(p => p.MainWindowTitle)
                .ToList();
            lblResult.Text = $"Số cửa sổ: {windows.Count}";
            foreach (var title in windows)
            {
                lstWindows.Items.Add(title);
            }
        }
    }
}
