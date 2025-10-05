using System;
using System.Drawing;
using System.Windows.Forms;

namespace MiniGame
{
    public partial class PingPongGame : Form
    {
        // Game objects
        private Rectangle ball;
        private Rectangle leftPaddle;
        private Rectangle rightPaddle;
        
        // Ball movement
        private int ballSpeedX = 5;
        private int ballSpeedY = 5;
        
        // Paddle movement
        private bool leftPaddleUp = false;
        private bool leftPaddleDown = false;
        private bool rightPaddleUp = false;
        private bool rightPaddleDown = false;
        
        // Game timer
        private System.Windows.Forms.Timer gameTimer = null!;
        
        // Score
        private int leftScore = 0;
        private int rightScore = 0;
        
        // Game dimensions
        private const int PADDLE_WIDTH = 15;
        private const int PADDLE_HEIGHT = 80;
        private const int BALL_SIZE = 15;
        private const int PADDLE_SPEED = 8;

        public PingPongGame()
        {
            InitializeComponent();
            InitializeGame();
        }

        private void InitializeComponent()
        {
            // Form settings
            this.Text = "Ping Pong Game";
            this.Size = new Size(800, 600);
            this.StartPosition = FormStartPosition.CenterScreen;
            this.BackColor = Color.Black;
            this.FormBorderStyle = FormBorderStyle.FixedSingle;
            this.MaximizeBox = false;
            
            // Enable double buffering to reduce flicker
            this.SetStyle(ControlStyles.AllPaintingInWmPaint | ControlStyles.UserPaint | ControlStyles.DoubleBuffer, true);
            
            // Set up event handlers
            this.Paint += PingPongGame_Paint;
            this.KeyDown += PingPongGame_KeyDown;
            this.KeyUp += PingPongGame_KeyUp;
            
            // Make form focusable
            this.KeyPreview = true;
        }

        private void InitializeGame()
        {
            // Initialize ball position (center of screen)
            ball = new Rectangle(ClientSize.Width / 2 - BALL_SIZE / 2, 
                               ClientSize.Height / 2 - BALL_SIZE / 2, 
                               BALL_SIZE, BALL_SIZE);
            
            // Initialize paddles
            leftPaddle = new Rectangle(30, ClientSize.Height / 2 - PADDLE_HEIGHT / 2, 
                                     PADDLE_WIDTH, PADDLE_HEIGHT);
            rightPaddle = new Rectangle(ClientSize.Width - 30 - PADDLE_WIDTH, 
                                      ClientSize.Height / 2 - PADDLE_HEIGHT / 2, 
                                      PADDLE_WIDTH, PADDLE_HEIGHT);
            
            // Set up game timer
            gameTimer = new System.Windows.Forms.Timer();
            gameTimer.Interval = 20; // ~50 FPS
            gameTimer.Tick += GameTimer_Tick;
            gameTimer.Start();
        }

        private void GameTimer_Tick(object? sender, EventArgs e)
        {
            // Move ball
            ball.X += ballSpeedX;
            ball.Y += ballSpeedY;
            
            // Ball collision with top and bottom walls
            if (ball.Y <= 0 || ball.Y >= ClientSize.Height - BALL_SIZE)
            {
                ballSpeedY = -ballSpeedY;
            }
            
            // Ball collision with paddles
            if (ball.IntersectsWith(leftPaddle) || ball.IntersectsWith(rightPaddle))
            {
                ballSpeedX = -ballSpeedX;
            }
            
            // Ball out of bounds (scoring)
            if (ball.X < 0)
            {
                rightScore++;
                ResetBall();
            }
            else if (ball.X > ClientSize.Width)
            {
                leftScore++;
                ResetBall();
            }
            
            // Move paddles
            if (leftPaddleUp && leftPaddle.Y > 0)
                leftPaddle.Y -= PADDLE_SPEED;
            if (leftPaddleDown && leftPaddle.Y < ClientSize.Height - PADDLE_HEIGHT)
                leftPaddle.Y += PADDLE_SPEED;
            if (rightPaddleUp && rightPaddle.Y > 0)
                rightPaddle.Y -= PADDLE_SPEED;
            if (rightPaddleDown && rightPaddle.Y < ClientSize.Height - PADDLE_HEIGHT)
                rightPaddle.Y += PADDLE_SPEED;
            
            // Redraw the form
            this.Invalidate();
        }

        private void ResetBall()
        {
            ball.X = ClientSize.Width / 2 - BALL_SIZE / 2;
            ball.Y = ClientSize.Height / 2 - BALL_SIZE / 2;
            
            // Random direction
            Random rand = new Random();
            ballSpeedX = rand.Next(0, 2) == 0 ? -5 : 5;
            ballSpeedY = rand.Next(-3, 4);
        }

        private void PingPongGame_Paint(object? sender, PaintEventArgs e)
        {
            Graphics g = e.Graphics;
            
            // Draw paddles
            g.FillRectangle(Brushes.White, leftPaddle);
            g.FillRectangle(Brushes.White, rightPaddle);
            
            // Draw ball
            g.FillEllipse(Brushes.White, ball);
            
            // Draw center line
            using (Pen pen = new Pen(Color.White, 2))
            {
                pen.DashStyle = System.Drawing.Drawing2D.DashStyle.Dash;
                g.DrawLine(pen, ClientSize.Width / 2, 0, ClientSize.Width / 2, ClientSize.Height);
            }
            
            // Draw scores
            using (Font font = new Font("Arial", 24, FontStyle.Bold))
            {
                string leftScoreText = leftScore.ToString();
                string rightScoreText = rightScore.ToString();
                
                SizeF leftScoreSize = g.MeasureString(leftScoreText, font);
                SizeF rightScoreSize = g.MeasureString(rightScoreText, font);
                
                g.DrawString(leftScoreText, font, Brushes.White, 
                           ClientSize.Width / 4 - leftScoreSize.Width / 2, 50);
                g.DrawString(rightScoreText, font, Brushes.White, 
                           3 * ClientSize.Width / 4 - rightScoreSize.Width / 2, 50);
            }
            
            // Draw instructions
            using (Font font = new Font("Arial", 12))
            {
                string instructions = "Left Player: W/S keys | Right Player: UP/DOWN arrow keys | ESC to exit";
                SizeF textSize = g.MeasureString(instructions, font);
                g.DrawString(instructions, font, Brushes.Gray, 
                           ClientSize.Width / 2 - textSize.Width / 2, ClientSize.Height - 30);
            }
        }

        private void PingPongGame_KeyDown(object? sender, KeyEventArgs e)
        {
            switch (e.KeyCode)
            {
                case Keys.W:
                    leftPaddleUp = true;
                    break;
                case Keys.S:
                    leftPaddleDown = true;
                    break;
                case Keys.Up:
                    rightPaddleUp = true;
                    break;
                case Keys.Down:
                    rightPaddleDown = true;
                    break;
                case Keys.Escape:
                    this.Close();
                    break;
            }
        }

        private void PingPongGame_KeyUp(object? sender, KeyEventArgs e)
        {
            switch (e.KeyCode)
            {
                case Keys.W:
                    leftPaddleUp = false;
                    break;
                case Keys.S:
                    leftPaddleDown = false;
                    break;
                case Keys.Up:
                    rightPaddleUp = false;
                    break;
                case Keys.Down:
                    rightPaddleDown = false;
                    break;
            }
        }

        protected override void OnFormClosed(FormClosedEventArgs e)
        {
            gameTimer?.Stop();
            gameTimer?.Dispose();
            base.OnFormClosed(e);
        }
    }
}