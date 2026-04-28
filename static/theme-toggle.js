// theme-toggle.js - زر الوضع الليلي/النهاري الموحد
(function() {
    // تطبيق الوضع المحفوظ
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
        document.body.classList.add('light-mode');
    } else if (savedTheme === 'dark') {
        document.body.classList.add('dark-mode');
    }
    
    // إنشاء الزر العائم
    const toggleBtn = document.createElement('button');
    toggleBtn.id = 'globalThemeToggle';
    toggleBtn.title = 'تغيير الوضع';
    toggleBtn.style.cssText = 'position: fixed; bottom: 100px; right: 30px; width: 50px; height: 50px; border-radius: 50%; background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); color: white; font-size: 22px; cursor: pointer; z-index: 9999; display: flex; align-items: center; justify-content: center; backdrop-filter: blur(10px); transition: all 0.3s;';
    
    function updateIcon() {
        if (document.body.classList.contains('dark-mode')) {
            toggleBtn.innerHTML = '☀️';
        } else if (document.body.classList.contains('light-mode')) {
            toggleBtn.innerHTML = '🌙';
        } else {
            toggleBtn.innerHTML = '🌓';
        }
    }
    
    updateIcon();
    
    toggleBtn.addEventListener('click', () => {
        if (document.body.classList.contains('dark-mode')) {
            document.body.classList.remove('dark-mode');
            document.body.classList.add('light-mode');
            localStorage.setItem('theme', 'light');
        } else if (document.body.classList.contains('light-mode')) {
            document.body.classList.remove('light-mode');
            document.body.classList.add('dark-mode');
            localStorage.setItem('theme', 'dark');
        } else {
            document.body.classList.add('dark-mode');
            localStorage.setItem('theme', 'dark');
        }
        updateIcon();
    });
    
    document.body.appendChild(toggleBtn);
})();