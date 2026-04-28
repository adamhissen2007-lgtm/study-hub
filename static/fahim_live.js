// fahim_live.js - المحرك المحلي الصاروخي (الأولوية للسرعة)
async function getFahimLiveResponse(message) {
    // ردود فورية للتفاعلات الإنسانية
    if (message.includes('شكرا') || message.includes('تسلم')) return "الشكر لله! 🚀 أنا في خدمتك.";
    if (message.includes('صباح الخير')) return "صباح النور! 🌅 جاهز لأسئلتك.";

    // الأولوية القصوى للنموذج المحلي (Ollama)
    console.log("⚡️ جاري معالجة السؤال محلياً...");
    try {
        const res = await fetch('/api/code-mentor', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({question: message, mode: 'chat'})
        });
        
        if (res.ok) {
            const data = await res.json();
            if (data.answer) return data.answer;
        }
    } catch (e) {
        console.error("Local AI Error:", e);
    }

    // لو فشل المحلي، نرجع null (والـ code_mentor.html هيتعامل معاها)
    return null;
}