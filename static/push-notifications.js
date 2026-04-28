// push-notifications.js - نظام الإشعارات
function requestNotificationPermission() {
  if (!('Notification' in window)) {
    console.log('المتصفح مش بيدعم الإشعارات');
    return;
  }
  
  Notification.requestPermission().then((permission) => {
    if (permission === 'granted') {
      console.log('✅ تم تفعيل الإشعارات');
      
      // تسجيل Push Manager
      navigator.serviceWorker.ready.then((registration) => {
        registration.pushManager.subscribe({
          userVisibleOnly: true,
          applicationServerKey: urlBase64ToUint8Array('YOUR_VAPID_PUBLIC_KEY')
        }).then((subscription) => {
          console.log('✅ تم الاشتراك في Push:', subscription);
          // إرسال الـ subscription للسيرفر
        }).catch((e) => {
          console.log('❌ فشل الاشتراك:', e);
        });
      });
    }
  });
}

function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding).replace(/\-/g, '+').replace(/_/g, '/');
  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);
  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

// إرسال إشعار تجريبي
function sendTestNotification() {
  if (Notification.permission === 'granted') {
    new Notification('📚 Study Hub', {
      body: 'الإشعارات شغالة! هتقدر تستقبل تنبيهات لما يتم رفع ملفات جديدة.',
      icon: '/static/favicon.ico',
      vibrate: [200, 100, 200]
    });
  }
}

// طلب الإذن عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', () => {
  setTimeout(requestNotificationPermission, 3000);
});