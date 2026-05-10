/**
 * Ultimate Hub Scripts - Study Hub AI Platform
 * المركز المتقدم - جميع الدوال التفاعلية
 */

// ==================== Utility Functions ====================
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `fixed top-20 right-4 z-50 px-4 py-2 rounded-lg shadow-lg text-white ${
        type === 'success' ? 'bg-green-600' : type === 'error' ? 'bg-red-600' : 'bg-blue-600'
    }`;
    toast.innerHTML = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = '<div class="ultimate-loader"></div><p class="text-center mt-3">جاري المعالجة...</p>';
    }
}

function hideLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = '';
    }
}

// ==================== Digital Twin Functions ====================
async function createDigitalTwin() {
    const name = document.getElementById('twinName')?.value;
    if (!name) {
        showToast('الرجاء إدخال اسم التوأم الرقمي', 'error');
        return;
    }
    
    showLoading('twinResult');
    
    try {
        const response = await fetch('/api/twin/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, personality: 'wizard' })
        });
        const data = await response.json();
        
        const resultDiv = document.getElementById('twinResult');
        if (resultDiv) {
            resultDiv.innerHTML = `
                <div class="text-center">
                    <div class="text-6xl mb-4">🧬✨</div>
                    <h3 class="text-xl font-bold text-amber-400 mb-2">تم إنشاء توأمك الرقمي!</h3>
                    <p class="text-gray-300">الاسم: ${data.bot?.name || name}</p>
                    <p class="text-green-400 mt-3">${data.message || 'استمتع برحلتك مع توأمك الرقمي!'}</p>
                </div>
            `;
            setTimeout(() => closeModal('digitalTwinModal'), 2000);
        }
    } catch (error) {
        showToast('حدث خطأ في إنشاء التوأم الرقمي', 'error');
    }
}

// ==================== Time Capsule Functions ====================
async function createTimeCapsule() {
    const concept = document.getElementById('capsuleConcept')?.value;
    const content = document.getElementById('capsuleContent')?.value;
    
    if (!concept || !content) {
        showToast('الرجاء ملء جميع الحقول', 'error');
        return;
    }
    
    showLoading('capsuleResult');
    
    try {
        const response = await fetch('/api/capsule/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ concept, content })
        });
        const data = await response.json();
        
        const resultDiv = document.getElementById('capsuleResult');
        if (resultDiv) {
            resultDiv.innerHTML = `
                <div class="text-center">
                    <div class="text-6xl mb-4">📦✨</div>
                    <h3 class="text-xl font-bold text-amber-400 mb-2">تم حفظ كبسولتك!</h3>
                    <p class="text-gray-300">ستُفتح بعد 6 أشهر</p>
                    <p class="text-green-400 mt-3">${data.message || 'هيا بنا نرى تطورك!'}</p>
                </div>
            `;
            setTimeout(() => closeModal('timeCapsuleModal'), 2000);
        }
    } catch (error) {
        showToast('حدث خطأ في حفظ الكبسولة', 'error');
    }
}

// ==================== Dream Weaver Functions ====================
async function weaveDream() {
    const dream = document.getElementById('dreamText')?.value;
    
    if (!dream) {
        showToast('الرجاء كتابة حلمك', 'error');
        return;
    }
    
    showLoading('dreamResult');
    
    try {
        const response = await fetch('/api/dream/weave', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ dream })
        });
        const data = await response.json();
        
        const resultDiv = document.getElementById('dreamResult');
        if (resultDiv) {
            let phasesHtml = '';
            if (data.personalized_plan?.phases) {
                phasesHtml = '<div class="mt-4 p-4 bg-gray-800 rounded-lg text-right"><strong>📋 خطتك:</strong><br>';
                data.personalized_plan.phases.forEach(phase => {
                    phasesHtml += `<p class="mt-2"><strong>${phase.name}</strong>: ${phase.duration}</p>`;
                });
                phasesHtml += '</div>';
            }
            
            resultDiv.innerHTML = `
                <div class="text-center">
                    <div class="text-6xl mb-4">💭✨</div>
                    <h3 class="text-xl font-bold text-amber-400 mb-2">تم تحليل حلمك!</h3>
                    <p>احتمالية النجاح: ${data.predictions?.success_probability || 'عالية'}%</p>
                    <p>الوقت المتوقع: ${data.predictions?.estimated_time || 'غير محدد'} سنوات</p>
                    ${phasesHtml}
                    <button onclick="closeModal('dreamWeaverModal')" class="ultimate-btn mt-4">حلمي في الطريق 🚀</button>
                </div>
            `;
        }
    } catch (error) {
        showToast('حدث خطأ في تحليل الحلم', 'error');
    }
}

// ==================== Creativity Accelerator Functions ====================
async function explodeIdea() {
    const idea = document.getElementById('ideaText')?.value;
    
    if (!idea) {
        showToast('الرجاء كتابة فكرتك', 'error');
        return;
    }
    
    showLoading('creativityResult');
    
    try {
        const response = await fetch('/api/creativity/explode', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ idea })
        });
        const data = await response.json();
        
        const resultDiv = document.getElementById('creativityResult');
        if (resultDiv) {
            let ideasHtml = '';
            if (data.top_10_ideas) {
                ideasHtml = '<div class="mt-4 p-4 bg-gray-800 rounded-lg text-right">';
                data.top_10_ideas.forEach((idea, i) => {
                    ideasHtml += `<p><strong>${i+1}.</strong> ${idea.idea}</p>`;
                });
                ideasHtml += '</div>';
            }
            
            resultDiv.innerHTML = `
                <div class="text-center">
                    <div class="text-6xl mb-4">💥✨</div>
                    <h3 class="text-xl font-bold text-amber-400 mb-2">تم توليد ${data.total_ideas_generated || 50} فكرة!</h3>
                    ${ideasHtml}
                    <button onclick="closeModal('creativityModal')" class="ultimate-btn mt-4">رائع! 💡</button>
                </div>
            `;
        }
    } catch (error) {
        showToast('حدث خطأ في توليد الأفكار', 'error');
    }
}

// ==================== Destiny Mapper Functions ====================
async function mapDestiny() {
    const gpa = document.getElementById('destinyGpa')?.value;
    const hours = document.getElementById('destinyHours')?.value;
    const major = document.getElementById('destinyMajor')?.value;
    
    if (!gpa || !hours || !major) {
        showToast('الرجاء ملء جميع الحقول', 'error');
        return;
    }
    
    showLoading('destinyResult');
    
    try {
        const response = await fetch('/api/destiny/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ gpa: parseFloat(gpa), weekly_study_hours: parseInt(hours), major })
        });
        const data = await response.json();
        
        const resultDiv = document.getElementById('destinyResult');
        if (resultDiv) {
            let timelineHtml = '';
            if (data.primary_path?.timeline) {
                timelineHtml = '<div class="mt-4 p-4 bg-gray-800 rounded-lg text-right"><strong>⏰ الجدول الزمني:</strong><br>';
                data.primary_path.timeline.forEach(m => {
                    timelineHtml += `<p class="mt-2">📅 ${m.year}: ${m.milestone}</p>`;
                });
                timelineHtml += '</div>';
            }
            
            resultDiv.innerHTML = `
                <div class="text-center">
                    <div class="text-6xl mb-4">🔮✨</div>
                    <h3 class="text-xl font-bold text-amber-400 mb-2">خريطة مستقبلك</h3>
                    <p>احتمالية النجاح: ${data.success_probability?.percentage || 75}%</p>
                    ${timelineHtml}
                    <button onclick="closeModal('destinyModal')" class="ultimate-btn mt-4">شكراً! أرى مستقبلي 🚀</button>
                </div>
            `;
        }
    } catch (error) {
        showToast('حدث خطأ في رسم خريطة المستقبل', 'error');
    }
}

// ==================== AI Actor Functions ====================
async function startAIconversation(characterId) {
    const characterNames = {
        einstein: 'ألبرت أينشتاين',
        alkhwarizmi: 'الخوارزمي',
        jobs: 'ستيف جوبز',
        musk: 'إيلون ماسك'
    };
    
    const characterIcons = {
        einstein: '🧙',
        alkhwarizmi: '🧮',
        jobs: '🍎',
        musk: '🚀'
    };
    
    Swal.fire({
        title: `🎭 التحدث مع ${characterNames[characterId]}`,
        html: `
            <div class="text-center">
                <div class="text-6xl mb-4">${characterIcons[characterId]}</div>
                <p class="mb-3">ماذا تريد أن تسأل ${characterNames[characterId]}؟</p>
                <input type="text" id="conversationQuestion" class="w-full p-3 rounded-xl bg-gray-800 text-white border border-purple-500" placeholder="اسأل العبقري...">
                <div id="conversationAnswer" class="mt-4"></div>
            </div>
        `,
        showConfirmButton: false,
        showCloseButton: true,
        width: '500px'
    });
    
    const inputInterval = setInterval(() => {
        const questionInput = document.getElementById('conversationQuestion');
        if (questionInput && !questionInput.hasListener) {
            questionInput.hasListener = true;
            questionInput.addEventListener('keypress', async (e) => {
                if (e.key === 'Enter') {
                    const question = questionInput.value;
                    if (!question) return;
                    
                    const answerDiv = document.getElementById('conversationAnswer');
                    answerDiv.innerHTML = '<div class="ultimate-loader"></div><p class="mt-2">جاري التفكير...</p>';
                    
                    setTimeout(() => {
                        const answers = {
                            einstein: [
                                `"${question}"... سؤال عميق! الخيال أهم من المعرفة. استمر في التساؤل والاستكشاف.`,
                                `فيزيائياً، هذا يتعلق بمبدأ النسبية. تذكر أن كل شيء نسبي في هذا الكون.`
                            ],
                            alkhwarizmi: [
                                `لحل "${question}"، دعنا نقسم المشكلة إلى خطوات صغيرة. هذا هو جوهر الخوارزميات.`,
                                `الرياضيات تخبرنا أن لكل مشكلة حلاً، فقط نحتاج إلى الصبر والمعادلة الصحيحة.`
                            ],
                            jobs: [
                                `Stay hungry, stay foolish! بخصوص "${question}"، الحل هو أن تثق بحدسك وتتبع شغفك.`,
                                `العمل العظيم يأتي من شغف لا من منطق. اسأل نفسك: هل هذا سيغير العالم؟`
                            ],
                            musk: [
                                `من الناحية التقنية، "${question}" ممكن. الفيزياء لا تمنعه، فقط نحتاج إلى الهندسة المناسبة.`,
                                `المستقبل متعدد الكواكب قد يحمل إجابة لـ "${question}". استمر في الحلم والعمل.`
                            ]
                        };
                        const answerList = answers[characterId] || answers.einstein;
                        const answer = answerList[Math.floor(Math.random() * answerList.length)];
                        answerDiv.innerHTML = `<div class="p-4 bg-gray-800 rounded-lg text-right">💬 ${answer}</div>`;
                    }, 1500);
                }
            });
        }
    }, 100);
}

// ==================== Tab Switching ====================
function switchTab(tabId) {
    document.querySelectorAll('.ultimate-tab-content').forEach(tab => {
        tab.style.display = 'none';
    });
    document.getElementById(`tab-${tabId}`).style.display = 'block';
    
    document.querySelectorAll('.ultimate-tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
}

// ==================== Modal Functions ====================
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.style.display = 'flex';
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.style.display = 'none';
}

// Close modal when clicking outside
window.onclick = function(event) {
    if (event.target.classList.contains('ultimate-modal')) {
        event.target.style.display = 'none';
    }
};

// ==================== Initialize Stars Background ====================
function initStars() {
    const starsContainer = document.createElement('div');
    starsContainer.className = 'ultimate-stars';
    document.body.appendChild(starsContainer);
    
    for (let i = 0; i < 100; i++) {
        const star = document.createElement('div');
        star.className = 'ultimate-star';
        star.style.width = Math.random() * 3 + 1 + 'px';
        star.style.height = star.style.width;
        star.style.left = Math.random() * 100 + '%';
        star.style.top = Math.random() * 100 + '%';
        star.style.animationDelay = Math.random() * 5 + 's';
        star.style.opacity = Math.random() * 0.5 + 0.2;
        starsContainer.appendChild(star);
    }
}

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    initStars();
    console.log('🚀 Ultimate Hub initialized!');
});