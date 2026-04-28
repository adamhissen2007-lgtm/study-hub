// fahim_controller.js - قلب "فهيم" النابض
// ========== أوامر التحكم في المنصة ==========
const FahimCommands = {
    open_tab: (tabName) => {
        const tabs = {
            'lectures': 0, 'sheets': 1, 'exams': 2, 
            'videos': 3, 'discussions': 4, 'fahim': 5
        };
        if (tabs[tabName] !== undefined) {
            const tabBtns = document.querySelectorAll('.tab-btn');
            if (tabBtns[tabs[tabName]]) {
                tabBtns[tabs[tabName]].click();
                return `✅ تم فتح تبويب ${tabName}`;
            }
        }
        return '❌ لم يتم العثور على التبويب';
    },
    
    search_files: async (query) => {
        try {
            const res = await fetch('/api/platform-control', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({action: 'search', param: query})
            });
            const data = await res.json();
            if (data.success && data.results.length > 0) {
                return `✅ تم العثور على ${data.count} ملف:\n${data.results.map(r => `📄 ${r.filename}`).join('\n')}`;
            }
            return '❌ لم يتم العثور على ملفات';
        } catch (e) {
            return '❌ فشل البحث';
        }
    },
    
    get_stats: async () => {
        try {
            const res = await fetch('/api/platform-control', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({action: 'stats'})
            });
            const data = await res.json();
            return `📊 إحصائياتك:\n⭐ النقاط: ${data.user_points}\n🏆 المستوى: ${data.user_level}\n📚 المواد: ${data.courses_count}\n📄 الملفات: ${data.materials_count}`;
        } catch (e) {
            return '❌ فشل جلب الإحصائيات';
        }
    },
    
    change_theme: (theme) => {
        document.body.classList.toggle('dark-mode', theme === 'dark');
        document.body.classList.toggle('light-mode', theme === 'light');
        localStorage.setItem('theme', theme);
        return `✅ تم تغيير الثيم إلى ${theme === 'dark' ? 'الليلي 🌙' : 'النهاري ☀️'}`;
    },
    
    help: () => {
        return `📋 الأوامر المتاحة:\n• افتح تبويب [المحاضرات/الشيتات/الامتحانات]\n• ابحث عن [اسم الملف]\n• إحصائياتي\n• غير الثيم لـ[ليلي/نهاري]\n• علمني [الموضوع]\n• شجعني\n• نظملي يومي\n• تحديني\n• سؤال سقراطي: [الموضوع]\n• ممكن نتكلم شوية؟`;
    },
    
    teach: (topic) => {
        return `🧑‍🏫 هشرحلك ${topic} بالتفصيل. اسألني أي سؤال عنه!`;
    },

    // ✅ ميزة جديدة: المعلم السقراطي
    socratic: () => {
        const questions = [
            "🤔 قبل ما أجاوبك، إيه اللي فهمته من السؤال ده لحد دلوقتي؟",
            "🧠 إيه رأيك؟ إيه الحل المحتمل من وجهة نظرك؟",
            "💡 فكرت تحل المسألة دي بإيه بالضبط؟ قول لي خطوات تفكيرك.",
            "🔍 إيه اللي يخلي الحل ده صح؟ وإيه اللي يخليه غلط؟",
            "📚 إيه المبادئ اللي ممكن تطبقها هنا من اللي درسته قبل كده؟",
            "🎯 لو كنت هتحل المسألة دي قدام دكتور، هتشرحها إزاي؟"
        ];
        return questions[Math.floor(Math.random() * questions.length)];
    },

    // ✅ ميزة جديدة: منظم المهام اليومي
    daily_planner: () => {
        const now = new Date();
        const hour = now.getHours();
        let greeting = '';
        if (hour < 12) greeting = 'صباح الخير 🌅';
        else if (hour < 18) greeting = 'مساء الخير ☀️';
        else greeting = 'مساء الخير 🌙';
        
        return `📅 ${greeting}! ده جدول مقترح ليومك:
        
🕗 8:00 - 9:00 | 📚 مراجعة سريعة (30 دقيقة)
🕘 9:00 - 11:00 | 🧠 مذاكرة مادة صعبة (ساعتين)
🕚 11:00 - 11:15 | ☕ استراحة
🕚 11:15 - 13:00 | 💻 حل تمارين ومسائل
🕐 13:00 - 14:00 | 🍽️ غدا وراحة
🕑 14:00 - 16:00 | 📖 قراءة وتلخيص
🕕 18:00 - 19:00 | 🏃 رياضة أو مشي
🕖 19:00 - 20:00 | 📝 مراجعة سريعة للي فات

💡 نصيحة: خد 5 دقايق راحة كل نص ساعة مذاكرة!`;
    },

    // ✅ ميزة جديدة: نظام التحديات
    challenge: () => {
        const challenges = [
            { title: '🏆 تحدي اليوم: حل 5 مسائل', desc: 'اختار 5 مسائل من المادة اللي بتذاكرها وحلهم. لو حليتهم كلهم صح، هتاخد 10 نقاط إضافية!', points: 10 },
            { title: '📝 تحدي اليوم: لخص محاضرة', desc: 'اختار أي محاضرة ولخصها في 5 نقاط رئيسية. ده هيساعدك تثبت المعلومات!', points: 8 },
            { title: '💡 تحدي اليوم: اشرح لزميل', desc: 'حاول تشرح مفهوم صعب لزميلك (أو حتى لنفسك بصوت عالي). الشرح بيقوي الفهم!', points: 12 },
            { title: '📚 تحدي اليوم: اقرأ 10 صفحات', desc: 'اقرأ 10 صفحات من أي كتاب دراسي ولخص اللي فهمته.', points: 7 },
            { title: '🎯 تحدي اليوم: اختبر نفسك', desc: 'حل امتحان قديم للمادة. ده هيخليك جاهز للامتحانات!', points: 15 }
        ];
        const c = challenges[Math.floor(Math.random() * challenges.length)];
        return `${c.title}\n\n${c.desc}\n\n⭐ المكافأة: ${c.points} نقطة!`;
    },

    // ✅ ميزة جديدة: اقتراحات ذكية مبنية على الوقت
    time_based_greeting: () => {
        const hour = new Date().getHours();
        if (hour < 12) return 'صباح الخير! 🌅 جاهز تبدأ يوم دراسي قوي؟ قول لي "نظملي يومي" وهساعدك!';
        if (hour < 18) return 'مساء النشاط! ☀️ إيه اللي بتذاكره دلوقتي؟ محتاج مساعدة في حاجة؟';
        return 'لسه شغال؟ 🌙 متنساش ترتاح كويس عشان تقدر تركز بكره. قول لي "إحصائياتي" عشان تشوف إنجازات النهاردة!';
    }
};

// ========== شخصيات "فهيم" المتعددة ==========
const FahimPersonas = {
    friendly: {
        name: 'فهيم الصديق',
        emoji: '😊',
        style: 'ودود ومشجع',
        intro: 'صاحبي! أنا هنا عشان أساعدك. متقلقش، مع بعض هنوصل لأعلى المستويات! 💪',
        responses: {
            success: ['عاش يا بطل! 🎉', 'كده أنت جامد! 💪', 'ممتاز يا أسطورة! 🌟'],
            error: ['ولا يهمك، جرب تاني! 💪', 'عادي، كلنا بنتعلم! 😊', 'مش مشكلة، أنا معاك! 🤗'],
            greeting: ['أهلاً يا صاحبي! 😊', 'وحشتني والله! 💙', 'نور الموقع كله! ✨']
        }
    },
    strict: {
        name: 'فهيم المعلم',
        emoji: '👨‍🏫',
        style: 'صارم وجاد',
        intro: 'أنا الدكتور فهيم. هنا نتعلم بجد. ركز وحضر نفسك! 📚',
        responses: {
            success: ['جيد. واصل التقدم.', 'مقبول. فيه أحسن.', 'لا بأس. راجع الدرس تاني.'],
            error: ['غير مقبول. ذاكر أكتر.', 'ده خطأ كبير. ركز!', 'أنت مش مركز. عيد المحاولة.'],
            greeting: ['حاضر للدرس؟', 'يلا نبدأ من غير تضييع وقت.', 'جهزت أدواتك؟']
        }
    },
    motivator: {
        name: 'فهيم المحفز',
        emoji: '🔥',
        style: 'حماسي وملهم',
        intro: 'أنت بطل! أنت قدها! مفيش حاجة تقف قدامك! خلينا نولع الدنيا! 🚀🔥',
        responses: {
            success: ['ده اللي أنا بتكلم عنه! 🔥', 'أنت أسطورة والله! 🚀', 'كده أنت بطل العالم! 💪🔥'],
            error: ['الفشل بداية النجاح! قوم كمل! 🔥', 'الأبطال بيتعلموا من أخطائهم! 💪', 'متوقفش! أنت قدها! 🚀'],
            greeting: ['يلا بينا نبدأ رحلة النجاح! 🔥', 'جاهز تكسر الدنيا النهاردة؟ 🚀', 'أنت أقوى مما تتخيل! 💪🔥']
        }
    }
};

let currentPersona = 'friendly';

// ========== تغيير شخصية "فهيم" ==========
function switchPersona(persona) {
    currentPersona = persona;
    const p = FahimPersonas[persona];
    return `✅ تم تغيير الشخصية إلى: ${p.name} ${p.emoji}\n${p.intro}`;
}

// ========== الحالة المزاجية ==========
function getEmotionalResponse(sentiment) {
    const persona = FahimPersonas[currentPersona];
    if (sentiment === 'success') {
        return persona.responses.success[Math.floor(Math.random() * persona.responses.success.length)];
    } else if (sentiment === 'error') {
        return persona.responses.error[Math.floor(Math.random() * persona.responses.error.length)];
    }
    return persona.responses.greeting[Math.floor(Math.random() * persona.responses.greeting.length)];
}

// ========== دالة تنفيذ أوامر "فهيم" ==========
async function executeFahimCommand(message) {
    const patterns = [
        { regex: /افتح تبويب (\S+)/, action: 'open_tab', param: 1 },
        { regex: /ابحث عن (.+)/, action: 'search_files', param: 1 },
        { regex: /إحصائياتي/, action: 'get_stats', param: null },
        { regex: /غير الثيم لـ(ليلي|نهاري)/, action: 'change_theme', param: 1 },
        { regex: /علمني (.+)/, action: 'teach', param: 1 },
        { regex: /شجعني/, action: 'motivate', param: null },
        { regex: /مساعدة/, action: 'help', param: null },
        { regex: /الأوامر/, action: 'help', param: null },
        { regex: /سؤال سقراطي/, action: 'socratic', param: null },
        { regex: /نظملي يومي/, action: 'daily_planner', param: null },
        { regex: /تحديني/, action: 'challenge', param: null },
        { regex: /ممكن نتكلم/, action: 'free_chat', param: null },
        { regex: /صباح|مساء/, action: 'time_greeting', param: null },
    ];

    for (let pattern of patterns) {
        const match = message.match(pattern.regex);
        if (match) {
            const action = pattern.action;
            let param = pattern.param ? (typeof pattern.param === 'number' ? match[pattern.param] : pattern.param) : null;
            
            if (action === 'change_theme') {
                param = param.includes('ليلي') ? 'dark' : 'light';
            }
            
            if (action === 'motivate') {
                return getEmotionalResponse('success');
            }
            
            if (action === 'free_chat') {
                return 'طبعاً! 🥰 أنا هنا عشانك. إيه اللي في بالك؟ تحكي لي عن يومك؟ ولا عايز نتناقش في موضوع معين؟ أو لو حابب تسأل عن حاجة في المنصة، أنا جاهز! 💙';
            }
            
            if (action === 'time_greeting') {
                return FahimCommands.time_based_greeting();
            }
            
            if (FahimCommands[action]) {
                if (param) {
                    return await FahimCommands[action](param);
                }
                return await FahimCommands[action]();
            }
        }
    }
    
    return null;
}