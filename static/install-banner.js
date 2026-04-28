// install-banner.js - بانر تثبيت التطبيق المخصص
let deferredPrompt;

window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    
    // إنشاء بانر التثبيت
    const banner = document.createElement('div');
    banner.id = 'pwaInstallBanner';
    banner.style.cssText = 'position: fixed; bottom: 0; left: 0; right: 0; background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; padding: 15px 20px; z-index: 100000; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 -5px 20px rgba(0,0,0,0.3); animation: slideUp 0.3s ease;';
    
    banner.innerHTML = `
        <div>
            <strong style="font-size: 16px;">📱 ثبت تطبيق Study Hub</strong>
            <p style="font-size: 12px; margin-top: 3px; opacity: 0.9;">وصول أسرع وتجربة أفضل بدون متصفح</p>
        </div>
        <div style="display: flex; gap: 10px;">
            <button id="installBtn" style="background: white; color: #6366f1; border: none; padding: 12px 25px; border-radius: 50px; font-weight: 700; cursor: pointer; font-size: 14px;">📥 تثبيت</button>
            <button id="dismissBtn" style="background: transparent; border: 1px solid rgba(255,255,255,0.5); color: white; padding: 12px 15px; border-radius: 50px; cursor: pointer; font-size: 14px;">✕</button>
        </div>
    `;
    
    document.body.appendChild(banner);
    
    document.getElementById('installBtn').addEventListener('click', async () => {
        deferredPrompt.prompt();
        const { outcome } = await deferredPrompt.userChoice;
        console.log(`✅ User response: ${outcome}`);
        deferredPrompt = null;
        banner.remove();
    });
    
    document.getElementById('dismissBtn').addEventListener('click', () => {
        banner.remove();
    });
});

window.addEventListener('appinstalled', () => {
    console.log('✅ تم تثبيت التطبيق بنجاح');
    const banner = document.getElementById('pwaInstallBanner');
    if (banner) banner.remove();
});