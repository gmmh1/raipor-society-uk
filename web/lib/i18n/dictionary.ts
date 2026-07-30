import type { Lang } from "./config";

/**
 * Flat dot-path translation table. Only static UI chrome and authored marketing
 * copy is translated — content coming from the API (events, documents, shop
 * products, etc.) is stored and shown in whatever language staff entered it.
 */
const en = {
  "nav.home": "Home",
  "nav.about": "About",
  "nav.programs": "Programs",
  "nav.events": "Events",
  "nav.blog": "News",
  "nav.shop": "Shop",
  "nav.contact": "Contact",
  "nav.donate": "Donate",
  "nav.signIn": "Sign in",
  "nav.join": "Join",
  "nav.memberSignIn": "Member sign in",

  "footer.about":
    "A community bringing people together through culture, learning, and collective progress. Unity, Culture, Friendship, Progress — always forward together.",
  "footer.explore": "Explore",
  "footer.aboutLink": "About the society",
  "footer.community": "Community",
  "footer.contactUs": "Contact us",
  "footer.rights": "All rights reserved.",
  "footer.registered": "Registered community organisation, United Kingdom.",

  "home.eyebrow": "Registered community organisation · United Kingdom",
  "home.heroTitlePre": "Unity, culture, and",
  "home.heroTitleEm": "progress",
  "home.heroTitlePost": "— together.",
  "home.heroBody":
    "Raipor Society UK brings people together through events, learning, and collaboration — celebrating our diversity while building strong bonds, encouraging personal growth, and working toward a better future for the whole community.",
  "home.joinCta": "Join the community",
  "home.programsCta": "See our programs",
  "home.pillarsEyebrow": "What we stand for",
  "home.pillarsTitle": "Four ideas hold everything we do together.",
  "home.pillar.unity.title": "Unity",
  "home.pillar.unity.copy":
    "One community across generations and backgrounds, gathered around shared roots and a shared future.",
  "home.pillar.culture.title": "Culture",
  "home.pillar.culture.copy":
    "Festivals, food, language, and tradition, kept alive and passed on through everyday community life.",
  "home.pillar.friendship.title": "Friendship",
  "home.pillar.friendship.copy":
    "A place to belong — new arrivals, long-time members, young people, and elders, all welcome at the table.",
  "home.pillar.progress.title": "Progress",
  "home.pillar.progress.copy":
    "Learning, mentorship, and mutual support that help every member and the community grow together.",
  "home.programsEyebrow": "Get involved",
  "home.programsTitle": "Programs built around the community's real needs.",
  "home.program.culture.tag": "Culture",
  "home.program.culture.title": "Festivals & celebrations",
  "home.program.culture.copy":
    "Seasonal gatherings and cultural festivals that bring the community together to celebrate shared heritage.",
  "home.program.youth.tag": "Youth",
  "home.program.youth.title": "Youth & education",
  "home.program.youth.copy":
    "Mentorship, language classes, and activities that help younger members build confidence and connection.",
  "home.program.welfare.tag": "Welfare",
  "home.program.welfare.title": "Community welfare",
  "home.program.welfare.copy":
    "Practical support for members and families navigating new challenges, from newcomers to elders.",
  "home.program.gatherings.tag": "Gatherings",
  "home.program.gatherings.title": "Regular meet-ups",
  "home.program.gatherings.copy":
    "Ongoing social and interest gatherings that keep the community connected between big events.",
  "home.ctaTitle": "Every member makes this community stronger.",
  "home.ctaBody":
    "Whether you're joining an event, becoming a member, or supporting our work, there's a place for you here.",
  "home.ctaContact": "Get in touch",
  "home.ctaDonate": "Ways to give",

  "about.eyebrow": "About us",
  "about.title": "A community, established for the long run.",
  "about.lede":
    "Raipor Society UK is a community organisation bringing people together through events, learning, and collaboration — celebrating our diversity while building strong bonds and encouraging personal growth and collective development for a better future. Always forward, together.",
  "about.workEyebrow": "How we work",
  "about.workTitle": "What guides the society day to day.",
  "about.value.open.title": "Open to everyone",
  "about.value.open.copy":
    "Every event, program, and welfare service is open to the whole community, regardless of age or background.",
  "about.value.member.title": "Run by members",
  "about.value.member.copy":
    "Decisions are made through open governance and member voting — this is a community organisation run for its members, by its members.",
  "about.value.lasting.title": "Built to last",
  "about.value.lasting.copy":
    "We invest in people, not just events — mentorship, safeguarding, and steady, patient community-building.",
  "about.governanceEyebrow": "Governance",
  "about.governanceTitle": "Member-led, transparently run.",
  "about.governanceBody":
    "Membership status, committee roles, and community votes are all handled through the society's own member portal, with an auditable record behind every decision — because trust is something we build in the open, not something we ask for.",
  "about.committeeTitle": "Current committee",
  "about.noCommittee": "Committee positions will be listed here once assigned.",
  "about.membersTitle": "Members",
  "about.noMembers": "Members who choose to share their profile publicly will appear here.",
  "about.timelineTitle": "Our timeline",
  "about.noTimeline": "Our history will be published here soon.",

  "programs.eyebrow": "Programs",
  "programs.title": "Community life, all year round.",
  "programs.lede":
    "Our programs exist to bring people together and help them grow — through culture, youth work, welfare, and shared learning.",
  "programs.culture.tag": "Culture",
  "programs.culture.title": "Festivals & celebrations",
  "programs.culture.copy":
    "Seasonal gatherings and cultural festivals that bring the whole community together to celebrate shared heritage, food, music, and tradition.",
  "programs.youth.tag": "Youth",
  "programs.youth.title": "Youth & education",
  "programs.youth.copy":
    "Mentorship, language classes, and structured activities that help younger members build confidence, skills, and a sense of belonging.",
  "programs.welfare.tag": "Welfare",
  "programs.welfare.title": "Community welfare",
  "programs.welfare.copy":
    "Practical, everyday support for members and families — from newcomers settling in to elders who need a helping hand.",
  "programs.gatherings.tag": "Gatherings",
  "programs.gatherings.title": "Regular meet-ups",
  "programs.gatherings.copy":
    "Ongoing social and interest-based gatherings that keep the community connected between the big annual events.",
  "programs.learning.tag": "Learning",
  "programs.learning.title": "Workshops & skills",
  "programs.learning.copy":
    "Practical sessions run by and for members, sharing skills that help people and the wider community grow.",
  "programs.governance.tag": "Governance",
  "programs.governance.title": "Community voice",
  "programs.governance.copy":
    "Open member voting and committee elections, so the direction of the society is always set by its members.",

  "contact.eyebrow": "Contact",
  "contact.title": "We'd love to hear from you.",
  "contact.lede":
    "Questions about membership, events, or how to get involved — reach out and a member of the committee will get back to you.",
  "contact.emailTitle": "Email us",
  "contact.emailBody": "The quickest way to reach the committee directly.",
  "contact.memberTitle": "Already a member?",
  "contact.memberBody": "Sign in to the member portal for events, documents, and voting.",
  "contact.memberSignIn": "Member sign in",

  "login.title": "Sign in",
  "login.subtitle": "Access your member or committee portal.",
  "login.username": "Username",
  "login.password": "Password",
  "login.submit": "Sign in",
  "login.submitting": "Signing in…",
  "login.back": "← Back to the public site",
  "login.error": "Sign in failed. Check your details and try again.",
  "login.networkError": "Couldn't reach the server. Please try again.",

  "events.eyebrow": "Events",
  "events.title": "Where the community gathers.",
  "events.lede":
    "From seasonal festivals to regular meet-ups, this is where we'll publish everything happening across the society.",
  "events.comingSoon": "Coming soon",
  "events.noneTitle": "No events published yet",
  "events.noneBody":
    "We're setting up our events calendar. Get in touch to be added to our updates list, and you'll hear about gatherings as soon as they're scheduled.",
  "events.cta": "Get event updates",
  "events.upcomingTitle": "Upcoming events",
  "events.signIn": "Sign in to register",

  "register.title": "Become a member",
  "register.subtitle": "Join the community — it only takes a minute.",
  "register.firstName": "First name",
  "register.lastName": "Last name",
  "register.username": "Username",
  "register.email": "Email",
  "register.dob": "Date of birth",
  "register.dobNote":
    "Members under 18 need a parent or guardian to confirm consent before their membership is activated.",
  "register.password": "Password",
  "register.passwordNote": "At least 10 characters.",
  "register.submit": "Create account",
  "register.submitting": "Creating account…",
  "register.haveAccount": "Already a member?",
  "register.signIn": "Sign in",
  "register.genericError": "Couldn't create your account.",
  "register.doneTitle": "Check your email",
  "register.doneBodyPre": "We've sent a verification link to",
  "register.doneBodyPost": "Follow it to activate your account, then sign in.",
  "register.goToSignIn": "Go to sign in",

  "donate.eyebrow": "Donate",
  "donate.title": "Give what you can — it goes straight back into the community.",
  "donate.lede":
    "Every donation supports our events, youth programs, and welfare work. Give securely online — no account needed.",
  "donate.thanks": "Thank you — your donation is processing. We're grateful for your support.",
  "donate.giveOnline": "Give online",
  "donate.makeADonation": "Make a donation",
  "donate.use.events.title": "Community events",
  "donate.use.events.copy": "Venue, food, and logistics for gatherings open to the whole community.",
  "donate.use.youth.title": "Youth programs",
  "donate.use.youth.copy": "Mentorship, classes, and activities for the society's younger members.",
  "donate.use.welfare.title": "Welfare support",
  "donate.use.welfare.copy": "Practical help for members and families who need it most.",

  "lang.switch": "Language",
};

const bn: Partial<Record<keyof typeof en, string>> = {
  "nav.home": "হোম",
  "nav.about": "আমাদের সম্পর্কে",
  "nav.programs": "কার্যক্রম",
  "nav.events": "ইভেন্ট",
  "nav.blog": "সংবাদ",
  "nav.shop": "শপ",
  "nav.contact": "যোগাযোগ",
  "nav.donate": "অনুদান",
  "nav.signIn": "সাইন ইন",
  "nav.join": "যোগ দিন",
  "nav.memberSignIn": "সদস্য সাইন ইন",

  "footer.about":
    "সংস্কৃতি, শিক্ষা এবং সম্মিলিত অগ্রগতির মাধ্যমে মানুষকে একত্রিত করা একটি কমিউনিটি। ঐক্য, সংস্কৃতি, বন্ধুত্ব, অগ্রগতি — সবসময় একসাথে সামনের দিকে।",
  "footer.explore": "অন্বেষণ",
  "footer.aboutLink": "সোসাইটি সম্পর্কে",
  "footer.community": "কমিউনিটি",
  "footer.contactUs": "যোগাযোগ করুন",
  "footer.rights": "সর্বস্বত্ব সংরক্ষিত।",
  "footer.registered": "নিবন্ধিত কমিউনিটি সংস্থা, যুক্তরাজ্য।",

  "home.eyebrow": "নিবন্ধিত কমিউনিটি সংস্থা · যুক্তরাজ্য",
  "home.heroTitlePre": "ঐক্য, সংস্কৃতি এবং",
  "home.heroTitleEm": "অগ্রগতি",
  "home.heroTitlePost": "— একসাথে।",
  "home.heroBody":
    "রাইপর সোসাইটি ইউকে ইভেন্ট, শিক্ষা এবং সহযোগিতার মাধ্যমে মানুষকে একত্রিত করে — আমাদের বৈচিত্র্যকে উদযাপন করার পাশাপাশি দৃঢ় বন্ধন গড়ে তোলে, ব্যক্তিগত উন্নতিকে উৎসাহিত করে এবং সমগ্র কমিউনিটির জন্য একটি উন্নত ভবিষ্যতের দিকে কাজ করে।",
  "home.joinCta": "কমিউনিটিতে যোগ দিন",
  "home.programsCta": "আমাদের কার্যক্রম দেখুন",
  "home.pillarsEyebrow": "আমরা যা বিশ্বাস করি",
  "home.pillarsTitle": "চারটি ধারণা আমাদের সব কাজকে একসাথে ধরে রাখে।",
  "home.pillar.unity.title": "ঐক্য",
  "home.pillar.unity.copy":
    "প্রজন্ম ও পটভূমি জুড়ে একটি কমিউনিটি, যা ভাগ করা শিকড় ও ভবিষ্যতের চারপাশে একত্রিত।",
  "home.pillar.culture.title": "সংস্কৃতি",
  "home.pillar.culture.copy":
    "উৎসব, খাবার, ভাষা এবং ঐতিহ্য, প্রতিদিনের কমিউনিটি জীবনের মাধ্যমে জীবন্ত ও প্রবাহিত।",
  "home.pillar.friendship.title": "বন্ধুত্ব",
  "home.pillar.friendship.copy":
    "একটি আপন জায়গা — নতুন আগত, দীর্ঘদিনের সদস্য, তরুণ ও প্রবীণ, সবাইকে স্বাগতম।",
  "home.pillar.progress.title": "অগ্রগতি",
  "home.pillar.progress.copy":
    "শিক্ষা, পরামর্শদান এবং পারস্পরিক সহায়তা যা প্রতিটি সদস্য ও কমিউনিটিকে একসাথে বেড়ে উঠতে সাহায্য করে।",
  "home.programsEyebrow": "যুক্ত হন",
  "home.programsTitle": "কমিউনিটির প্রকৃত প্রয়োজন অনুযায়ী গড়া কার্যক্রম।",
  "home.program.culture.tag": "সংস্কৃতি",
  "home.program.culture.title": "উৎসব ও উদযাপন",
  "home.program.culture.copy":
    "মৌসুমি অনুষ্ঠান ও সাংস্কৃতিক উৎসব যা কমিউনিটিকে একসাথে ভাগ করা ঐতিহ্য উদযাপন করতে একত্রিত করে।",
  "home.program.youth.tag": "যুব",
  "home.program.youth.title": "যুব ও শিক্ষা",
  "home.program.youth.copy":
    "পরামর্শদান, ভাষা ক্লাস এবং কার্যক্রম যা তরুণ সদস্যদের আত্মবিশ্বাস ও সংযোগ গড়তে সাহায্য করে।",
  "home.program.welfare.tag": "কল্যাণ",
  "home.program.welfare.title": "কমিউনিটি কল্যাণ",
  "home.program.welfare.copy":
    "নতুন থেকে প্রবীণ পর্যন্ত, নতুন চ্যালেঞ্জ মোকাবিলাকারী সদস্য ও পরিবারের জন্য ব্যবহারিক সহায়তা।",
  "home.program.gatherings.tag": "সমাবেশ",
  "home.program.gatherings.title": "নিয়মিত সমাবেশ",
  "home.program.gatherings.copy":
    "চলমান সামাজিক ও আগ্রহভিত্তিক সমাবেশ যা বড় ইভেন্টের মাঝে কমিউনিটিকে সংযুক্ত রাখে।",
  "home.ctaTitle": "প্রতিটি সদস্য এই কমিউনিটিকে আরও শক্তিশালী করে তোলে।",
  "home.ctaBody":
    "আপনি ইভেন্টে যোগ দিচ্ছেন, সদস্য হচ্ছেন, বা আমাদের কাজকে সমর্থন করছেন — এখানে আপনার জন্য একটি জায়গা আছে।",
  "home.ctaContact": "যোগাযোগ করুন",
  "home.ctaDonate": "দান করার উপায়",

  "about.eyebrow": "আমাদের সম্পর্কে",
  "about.title": "দীর্ঘমেয়াদের জন্য প্রতিষ্ঠিত একটি কমিউনিটি।",
  "about.lede":
    "রাইপর সোসাইটি ইউকে একটি কমিউনিটি সংস্থা যা ইভেন্ট, শিক্ষা এবং সহযোগিতার মাধ্যমে মানুষকে একত্রিত করে — আমাদের বৈচিত্র্য উদযাপন করে দৃঢ় বন্ধন গড়ে তোলে এবং একটি উন্নত ভবিষ্যতের জন্য ব্যক্তিগত ও সম্মিলিত উন্নয়নকে উৎসাহিত করে। সবসময় সামনের দিকে, একসাথে।",
  "about.workEyebrow": "আমরা যেভাবে কাজ করি",
  "about.workTitle": "প্রতিদিন সোসাইটিকে যা পরিচালনা করে।",
  "about.value.open.title": "সবার জন্য উন্মুক্ত",
  "about.value.open.copy":
    "বয়স বা পটভূমি নির্বিশেষে প্রতিটি ইভেন্ট, কার্যক্রম এবং কল্যাণ সেবা সমগ্র কমিউনিটির জন্য উন্মুক্ত।",
  "about.value.member.title": "সদস্যদের দ্বারা পরিচালিত",
  "about.value.member.copy":
    "উন্মুক্ত পরিচালনা ও সদস্য ভোটের মাধ্যমে সিদ্ধান্ত নেওয়া হয় — এটি সদস্যদের জন্য, সদস্যদের দ্বারা পরিচালিত একটি কমিউনিটি সংস্থা।",
  "about.value.lasting.title": "টেকসই করে গড়া",
  "about.value.lasting.copy":
    "আমরা শুধু ইভেন্টে নয়, মানুষে বিনিয়োগ করি — পরামর্শদান, সুরক্ষা এবং স্থির, ধৈর্যশীল কমিউনিটি গঠন।",
  "about.governanceEyebrow": "পরিচালনা",
  "about.governanceTitle": "সদস্য-নেতৃত্বাধীন, স্বচ্ছভাবে পরিচালিত।",
  "about.governanceBody":
    "সদস্যপদের অবস্থা, কমিটির ভূমিকা এবং কমিউনিটি ভোট সবকিছুই সোসাইটির নিজস্ব সদস্য পোর্টালের মাধ্যমে পরিচালিত হয়, প্রতিটি সিদ্ধান্তের পেছনে একটি নিরীক্ষণযোগ্য রেকর্ড সহ — কারণ বিশ্বাস এমন কিছু যা আমরা প্রকাশ্যে গড়ে তুলি, চেয়ে নিই না।",
  "about.committeeTitle": "বর্তমান কমিটি",
  "about.noCommittee": "কমিটির পদগুলি নির্ধারণ হলে এখানে তালিকাভুক্ত করা হবে।",
  "about.membersTitle": "সদস্যবৃন্দ",
  "about.noMembers": "যেসব সদস্য তাদের প্রোফাইল প্রকাশ্যে শেয়ার করতে চান তারা এখানে প্রদর্শিত হবেন।",
  "about.timelineTitle": "আমাদের সময়রেখা",
  "about.noTimeline": "আমাদের ইতিহাস শীঘ্রই এখানে প্রকাশিত হবে।",

  "programs.eyebrow": "কার্যক্রম",
  "programs.title": "সারা বছর জুড়ে কমিউনিটি জীবন।",
  "programs.lede":
    "আমাদের কার্যক্রমের উদ্দেশ্য মানুষকে একত্রিত করা এবং তাদের বেড়ে উঠতে সাহায্য করা — সংস্কৃতি, যুব কাজ, কল্যাণ এবং ভাগ করা শিক্ষার মাধ্যমে।",
  "programs.culture.tag": "সংস্কৃতি",
  "programs.culture.title": "উৎসব ও উদযাপন",
  "programs.culture.copy":
    "মৌসুমি অনুষ্ঠান ও সাংস্কৃতিক উৎসব যা সমগ্র কমিউনিটিকে ভাগ করা ঐতিহ্য, খাবার, সংগীত ও প্রথা উদযাপন করতে একত্রিত করে।",
  "programs.youth.tag": "যুব",
  "programs.youth.title": "যুব ও শিক্ষা",
  "programs.youth.copy":
    "পরামর্শদান, ভাষা ক্লাস এবং কাঠামোগত কার্যক্রম যা তরুণ সদস্যদের আত্মবিশ্বাস, দক্ষতা ও অন্তর্ভুক্তির অনুভূতি গড়তে সাহায্য করে।",
  "programs.welfare.tag": "কল্যাণ",
  "programs.welfare.title": "কমিউনিটি কল্যাণ",
  "programs.welfare.copy":
    "নতুন করে বসবাসকারী থেকে সাহায্যের প্রয়োজন এমন প্রবীণ পর্যন্ত, সদস্য ও পরিবারের জন্য ব্যবহারিক, প্রাত্যহিক সহায়তা।",
  "programs.gatherings.tag": "সমাবেশ",
  "programs.gatherings.title": "নিয়মিত সমাবেশ",
  "programs.gatherings.copy":
    "চলমান সামাজিক ও আগ্রহভিত্তিক সমাবেশ যা বড় বার্ষিক ইভেন্টগুলোর মাঝে কমিউনিটিকে সংযুক্ত রাখে।",
  "programs.learning.tag": "শিক্ষা",
  "programs.learning.title": "কর্মশালা ও দক্ষতা",
  "programs.learning.copy":
    "সদস্যদের দ্বারা ও সদস্যদের জন্য পরিচালিত ব্যবহারিক সেশন, যা মানুষ ও বৃহত্তর কমিউনিটিকে বেড়ে উঠতে সাহায্য করে এমন দক্ষতা ভাগ করে।",
  "programs.governance.tag": "পরিচালনা",
  "programs.governance.title": "কমিউনিটির কণ্ঠস্বর",
  "programs.governance.copy":
    "উন্মুক্ত সদস্য ভোট ও কমিটি নির্বাচন, যাতে সোসাইটির দিকনির্দেশনা সবসময় এর সদস্যরা নির্ধারণ করে।",

  "contact.eyebrow": "যোগাযোগ",
  "contact.title": "আপনার কাছ থেকে শুনতে চাই।",
  "contact.lede":
    "সদস্যপদ, ইভেন্ট, বা যুক্ত হওয়ার উপায় নিয়ে প্রশ্ন — যোগাযোগ করুন, কমিটির একজন সদস্য আপনার সাথে যোগাযোগ করবেন।",
  "contact.emailTitle": "আমাদের ইমেইল করুন",
  "contact.emailBody": "সরাসরি কমিটির সাথে যোগাযোগের দ্রুততম উপায়।",
  "contact.memberTitle": "ইতিমধ্যে সদস্য?",
  "contact.memberBody": "ইভেন্ট, নথি এবং ভোটের জন্য সদস্য পোর্টালে সাইন ইন করুন।",
  "contact.memberSignIn": "সদস্য সাইন ইন",

  "login.title": "সাইন ইন",
  "login.subtitle": "আপনার সদস্য বা কমিটি পোর্টাল অ্যাক্সেস করুন।",
  "login.username": "ইউজারনেম",
  "login.password": "পাসওয়ার্ড",
  "login.submit": "সাইন ইন",
  "login.submitting": "সাইন ইন হচ্ছে…",
  "login.back": "← পাবলিক সাইটে ফিরে যান",
  "login.error": "সাইন ইন ব্যর্থ হয়েছে। আপনার তথ্য যাচাই করে আবার চেষ্টা করুন।",
  "login.networkError": "সার্ভারে পৌঁছানো যায়নি। আবার চেষ্টা করুন।",

  "events.eyebrow": "ইভেন্ট",
  "events.title": "যেখানে কমিউনিটি একত্রিত হয়।",
  "events.lede":
    "মৌসুমি উৎসব থেকে নিয়মিত সমাবেশ পর্যন্ত, সোসাইটি জুড়ে যা কিছু ঘটছে তা এখানে প্রকাশ করা হবে।",
  "events.comingSoon": "শীঘ্রই আসছে",
  "events.noneTitle": "এখনও কোনো ইভেন্ট প্রকাশিত হয়নি",
  "events.noneBody":
    "আমরা আমাদের ইভেন্ট ক্যালেন্ডার প্রস্তুত করছি। আমাদের আপডেট তালিকায় যুক্ত হতে যোগাযোগ করুন, সমাবেশের সময়সূচী নির্ধারিত হওয়ার সাথে সাথেই আপনি জানতে পারবেন।",
  "events.cta": "ইভেন্ট আপডেট পান",
  "events.upcomingTitle": "আসন্ন ইভেন্ট",
  "events.signIn": "নিবন্ধনের জন্য সাইন ইন করুন",

  "register.title": "সদস্য হন",
  "register.subtitle": "কমিউনিটিতে যোগ দিন — মাত্র এক মিনিট সময় লাগবে।",
  "register.firstName": "প্রথম নাম",
  "register.lastName": "শেষ নাম",
  "register.username": "ইউজারনেম",
  "register.email": "ইমেইল",
  "register.dob": "জন্ম তারিখ",
  "register.dobNote":
    "১৮ বছরের নিচে সদস্যদের সদস্যপদ সক্রিয় হওয়ার আগে একজন পিতা-মাতা বা অভিভাবকের সম্মতি নিশ্চিত করতে হবে।",
  "register.password": "পাসওয়ার্ড",
  "register.passwordNote": "কমপক্ষে ১০ অক্ষর।",
  "register.submit": "অ্যাকাউন্ট তৈরি করুন",
  "register.submitting": "অ্যাকাউন্ট তৈরি হচ্ছে…",
  "register.haveAccount": "ইতিমধ্যে সদস্য?",
  "register.signIn": "সাইন ইন",
  "register.genericError": "আপনার অ্যাকাউন্ট তৈরি করা যায়নি।",
  "register.doneTitle": "আপনার ইমেইল দেখুন",
  "register.doneBodyPre": "আমরা একটি যাচাইকরণ লিংক পাঠিয়েছি",
  "register.doneBodyPost": "আপনার অ্যাকাউন্ট সক্রিয় করতে এটি অনুসরণ করুন, তারপর সাইন ইন করুন।",
  "register.goToSignIn": "সাইন ইনে যান",

  "donate.eyebrow": "অনুদান",
  "donate.title": "আপনি যা পারেন দান করুন — এটি সরাসরি কমিউনিটিতে ফিরে যায়।",
  "donate.lede":
    "প্রতিটি অনুদান আমাদের ইভেন্ট, যুব কার্যক্রম এবং কল্যাণ কাজকে সমর্থন করে। নিরাপদে অনলাইনে দান করুন — কোনো অ্যাকাউন্টের প্রয়োজন নেই।",
  "donate.thanks": "ধন্যবাদ — আপনার অনুদান প্রক্রিয়াধীন। আপনার সহায়তার জন্য আমরা কৃতজ্ঞ।",
  "donate.giveOnline": "অনলাইনে দান করুন",
  "donate.makeADonation": "একটি অনুদান দিন",
  "donate.use.events.title": "কমিউনিটি ইভেন্ট",
  "donate.use.events.copy": "সমগ্র কমিউনিটির জন্য উন্মুক্ত সমাবেশের স্থান, খাবার এবং ব্যবস্থাপনা।",
  "donate.use.youth.title": "যুব কার্যক্রম",
  "donate.use.youth.copy": "সোসাইটির তরুণ সদস্যদের জন্য পরামর্শদান, ক্লাস এবং কার্যক্রম।",
  "donate.use.welfare.title": "কল্যাণ সহায়তা",
  "donate.use.welfare.copy": "যাদের সবচেয়ে বেশি প্রয়োজন এমন সদস্য ও পরিবারের জন্য ব্যবহারিক সহায়তা।",

  "lang.switch": "ভাষা",
};

export type DictKey = keyof typeof en;

const tables: Record<Lang, Partial<Record<DictKey, string>>> = { en, bn };

export function translate(lang: Lang, key: DictKey): string {
  return tables[lang]?.[key] ?? en[key] ?? key;
}
