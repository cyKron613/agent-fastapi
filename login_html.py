# Login page HTML
LOGIN_HTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Empower Platform - 登录</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            position: relative;
            overflow: hidden;
            margin: 0;
            padding: 0;
        }

        /* 动态流体背景容器 */
        #fluidBgContainer {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            pointer-events: none;
        }

        .login-container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            padding: 40px;
            width: 420px;
            max-width: 90vw;
            box-shadow: 
                0 20px 40px rgba(0, 0, 0, 0.1),
                0 0 0 1px rgba(255, 255, 255, 0.2);
            position: relative;
            animation: slideUp 0.6s ease-out;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }

        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .logo-container {
            text-align: center;
            margin-bottom: 30px;
        }

        .logo {
            width: 80px;
            height: 80px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 20px;
            margin: 0 auto 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        }

        .logo::after {
            content: "🐬";
            font-size: 40px;
            filter: brightness(0) invert(1);
        }

        .welcome-text {
            font-size: 28px;
            font-weight: 700;
            color: #2d3748;
            margin-bottom: 8px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .subtitle {
            color: #718096;
            font-size: 16px;
            margin-bottom: 30px;
        }

        .form-group {
            margin-bottom: 24px;
            position: relative;
        }

        .input-wrapper {
            position: relative;
        }

        .input-icon {
            position: absolute;
            left: 16px;
            top: 50%;
            transform: translateY(-50%);
            color: #a0aec0;
            z-index: 2;
        }

        label {
            display: block;
            margin-bottom: 8px;
            color: #4a5568;
            font-weight: 600;
            font-size: 14px;
        }

        input {
            width: 100%;
            padding: 16px 16px 16px 48px;
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            font-size: 16px;
            background: #ffffff;
            transition: all 0.3s ease;
            outline: none;
        }

        input:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            transform: translateY(-1px);
        }

        input:focus + .input-icon {
            color: #667eea;
        }

        .login-button {
            width: 100%;
            padding: 16px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .login-button::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.5s;
        }

        .login-button:hover::before {
            left: 100%;
        }

        .login-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4);
        }

        .login-button:active {
            transform: translateY(0);
        }

        .error-message {
            background: #fed7e2;
            color: #c53030;
            padding: 12px 16px;
            border-radius: 8px;
            margin-bottom: 20px;
            border-left: 4px solid #e53e3e;
            animation: shake 0.5s ease-in-out;
        }

        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-5px); }
            75% { transform: translateX(5px); }
        }

        .footer-text {
            text-align: center;
            margin-top: 30px;
            color: #718096;
            font-size: 14px;
        }

        .powered-by {
            margin-top: 20px;
            text-align: center;
            color: #a0aec0;
            font-size: 12px;
        }

        /* 响应式设计 */
        @media (max-width: 480px) {
            .login-container {
                padding: 30px 20px;
                margin: 20px;
            }
            
            .welcome-text {
                font-size: 24px;
            }
        }

        /* 加载动画 */
        .loading {
            pointer-events: none;
        }

        .loading .login-button {
            background: #a0aec0;
            cursor: not-allowed;
        }

        .loading .login-button::after {
            content: '';
            width: 20px;
            height: 20px;
            border: 2px solid #ffffff;
            border-top: 2px solid transparent;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            display: inline-block;
            margin-left: 10px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <!-- 动态流体背景容器 -->
    <div id="fluidBgContainer"></div>

    <div class="login-container">
        <div class="logo-container">
            <div class="logo"></div>
            <h1 class="welcome-text">AI Empower Platform</h1>
            <p class="subtitle">登录访问 API 文档</p>
        </div>

        <form action="/login" method="post" id="loginForm">
            <div class="form-group">
                <label for="username">用户名</label>
                <div class="input-wrapper">
                    <div class="input-icon">👤</div>
                    <input type="text" id="username" name="username" required placeholder="请输入用户名">
                </div>
            </div>
            
            <div class="form-group">
                <label for="password">密码</label>
                <div class="input-wrapper">
                    <div class="input-icon">🔒</div>
                    <input type="password" id="password" name="password" required placeholder="请输入密码">
                </div>
            </div>
            
            <button type="submit" class="login-button">
                <span class="button-text">登录</span>
            </button>
        </form>

        <div class="footer-text">
            安全访问您的 API 文档
        </div>
        
        <div class="powered-by">
            Powered by Hi-Dolphin AI System
        </div>
    </div>

    <!-- 引入动态流体背景JS -->
    <script src="/static/AestheticFluidBg.min.js"></script>
    
    <script>
        // 初始化动态流体背景
        document.addEventListener('DOMContentLoaded', function() {
            let colorbg = new Color4Bg.AestheticFluidBg({
                dom: "fluidBgContainer",
                colors: ["#00ff62","#7d4cc8","#4053e2","#223dd8","#27E224","#00fbff"],
                loop: true
            });
        });
        
        // 添加表单提交动画
        document.getElementById('loginForm').addEventListener('submit', function(e) {
            const button = document.querySelector('.login-button');
            const buttonText = document.querySelector('.button-text');
            const container = document.querySelector('.login-container');
            
            // 添加加载状态
            container.classList.add('loading');
            buttonText.textContent = '登录中...';
        });

        // 输入框焦点效果
        const inputs = document.querySelectorAll('input');
        inputs.forEach(input => {
            input.addEventListener('focus', function() {
                this.parentElement.style.transform = 'scale(1.02)';
            });
            
            input.addEventListener('blur', function() {
                this.parentElement.style.transform = 'scale(1)';
            });
        });

        // 键盘快捷键支持
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && e.ctrlKey) {
                document.getElementById('loginForm').submit();
            }
        });
    </script>
</body>
</html>
"""
