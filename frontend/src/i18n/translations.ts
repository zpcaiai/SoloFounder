export type Lang = "en" | "zh";

export const translations = {
  en: {
    // Brand
    brand: "RevenuePilot",
    pageTitle: "RevenuePilot OS",
    headerTitle: "Solo Founder OS Console",

    // Nav
    nav_dashboard: "Dashboard",
    nav_skills: "Skills",
    nav_workflows: "Workflows",
    nav_history: "History",
    nav_settings: "Settings",

    // Sidebar info
    user: "User",
    project: "Project",
    api: "API",
    sameOrigin: "same origin",

    // Header status
    authenticated: "Authenticated",
    noApiKey: "No API key",

    // Language toggle
    langToggle: "中文",

    // Dashboard
    loadingDashboard: "Loading dashboard…",
    failedDashboard: "Failed to load dashboard",
    serviceHealth: "Service health",
    database: "Database",
    skillRuns: "Skill runs",
    workflowRuns: "Workflow runs",
    metrics: "Metrics",
    unknown: "unknown",

    // Skills
    skill: "Skill",
    selectSkill: "Select skill",
    inputPayload: "Input payload (JSON)",
    skillInputPayload: "Skill input payload",
    running: "Running…",
    runSkill: "Run skill",
    result: "Result",
    failedSkills: "Failed to load skills",

    // Workflows
    ideaToOffer: "Idea to Offer",
    dealToDelivery: "Deal to Delivery",
    contentToProduct: "Content to Product",
    ideaToOfferDesc: "Diagnose founder profile, select niche, validate market, and productize an offer.",
    dealToDeliveryDesc: "Coach a CRM deal, write a proposal, and plan the delivery project.",
    contentToProductDesc: "Turn knowledge assets into a productized offer.",
    workflowInputPayload: "Workflow input payload (JSON)",
    runWorkflow: "Run workflow",

    // History
    loadingHistory: "Loading history…",
    failedHistory: "Failed to load history",
    runs: "Runs",
    refreshHistory: "Refresh history",
    noRunsYet: "No runs yet.",
    details: "Details",
    selectRunToView: "Select a run to view details.",

    // Settings
    apiBaseUrl: "API base URL",
    apiBaseUrlPlaceholder: "Leave empty for same origin",
    apiBaseUrlHint: "For local dev with Vite proxy, keep this empty. For a remote backend, enter the full URL.",
    userId: "User ID",
    userIdHint: "Required in production as X-User-Id header.",
    apiKey: "API key",
    apiKeyHint: "Required in production as X-API-Key header.",
    defaultProjectId: "Default project ID",
    saveSettings: "Save settings",
    settingsSaved: "Settings saved.",
    testConnection: "Test connection",
    connectionOk: "Connection verified.",
    connectionFailed: "Connection failed",
    showApiKey: "Show API key",
    hideApiKey: "Hide API key",

    // Business nav
    nav_projects: "Projects",
    nav_ideas: "Ideas",
    nav_personas: "Personas",
    nav_offers: "Offers",
    nav_landing_pages: "Landing Pages",
    nav_outreach: "Outreach",
    nav_leads: "Leads",
    nav_deals: "Deals",
    nav_proposals: "Proposals",
    nav_delivery: "Delivery",
    nav_revenue: "Revenue",
    nav_business_dashboard: "Overview",

    // Common CRUD
    loading: "Loading…",
    create: "Create",
    update: "Update",
    delete: "Delete",
    save: "Save",
    cancel: "Cancel",
    edit: "Edit",
    confirmDelete: "Are you sure you want to delete this item?",
    noData: "No data yet.",
    name: "Name",
    status: "Status",
    actions: "Actions",
    data: "Data",
    created: "Created",
    updated: "Updated",
    selectProjectFirst: "Please select a project from Projects or Settings first.",
    errorOccurred: "An error occurred",

    // Projects
    projectsTitle: "Projects",
    projectName: "Project Name",
    projectNamePlaceholder: "My solo founder project",
    projectDescription: "Description",
    createProject: "Create Project",
    noProjects: "No projects yet. Create one to get started.",
    useProject: "Use project",
    currentProject: "Current",
    projectSelected: "Current project updated.",

    // Ideas
    ideasTitle: "Ideas",
    generateIdeas: "Generate Ideas",
    convertToOffer: "Convert to Offer",
    ideaTitle: "Title",
    ideaSummary: "Summary",
    noIdeas: "No ideas yet. Generate some with AI!",

    // Personas
    personasTitle: "Customer Personas",
    generatePersona: "Generate Persona",
    generateInterview: "Generate Interview",
    personaName: "Persona Name",
    personaRole: "Role",
    personaBusinessType: "Business Type",
    personaDemographics: "Demographics",
    personaPains: "Pain Points",
    noPersonas: "No personas yet. Generate one with AI!",

    // Offers
    offersTitle: "Offers",
    generateLandingPage: "Generate Landing Page",
    generateOutreachKit: "Generate Outreach Kit",
    offerName: "Offer Name",
    offerPrice: "Price",
    offerTargetCustomer: "Target Customer",
    offerDescription: "Description",
    noOffers: "No offers yet. Convert an idea or create one!",

    // Landing Pages
    landingPagesTitle: "Landing Pages",
    publish: "Publish",
    unpublish: "Unpublish",
    landingPageTitle: "Page Title",
    landingPageStatus: "Status",
    landingPageUrl: "URL",
    noLandingPages: "No landing pages yet.",

    // Outreach
    outreachTitle: "Outreach Assets",
    approveOutreach: "Approve",
    outreachChannel: "Channel",
    outreachSubject: "Subject",
    outreachStatus: "Status",
    noOutreach: "No outreach assets yet.",

    // Leads
    leadsTitle: "Leads",
    leadName: "Lead Name",
    leadSource: "Source",
    leadStatus: "Status",
    noLeads: "No leads yet.",

    // Deals
    dealsTitle: "Deals",
    markWon: "Mark Won",
    markLost: "Mark Lost",
    generateProposal: "Generate Proposal",
    generateDeliveryProject: "Generate Delivery Project",
    dealTitle: "Deal Title",
    dealValue: "Value",
    dealStage: "Stage",
    noDeals: "No deals yet.",

    // Proposals
    proposalsTitle: "Proposals",
    proposalTitle: "Proposal Title",
    proposalStatus: "Status",
    noProposals: "No proposals yet.",

    // Delivery
    deliveryTitle: "Delivery Projects",
    deliveryProjectTitle: "Project Title",
    deliveryStatus: "Status",
    deliveryTasks: "Tasks",
    addTask: "Add Task",
    taskTitle: "Task Title",
    taskStatus: "Task Status",
    noDeliveryProjects: "No delivery projects yet.",
    noTasks: "No tasks yet.",

    // Revenue
    revenueTitle: "Revenue Records",
    revenueAmount: "Amount",
    revenueSource: "Source",
    revenueDate: "Date",
    totalRevenue: "Total Revenue",
    noRevenue: "No revenue records yet.",

    // Business Dashboard
    overviewTitle: "Business Overview",
    totalRevenueLabel: "Total Revenue",
    activeLeads: "Active Leads",
    openDeals: "Open Deals",
    activeOffers: "Active Offers",
    openDelivery: "Open Delivery Projects",
    nextActions: "Next Actions",
    noNextActions: "All caught up! No pending actions.",

    // Error boundary
    errorTitle: "Something went wrong",
    errorBody: "The console hit an unexpected error. Your data is safe \u2014 reloading usually fixes it.",
    errorDetails: "Technical details",
    errorReload: "Reload console",
    close: "Close",
  },
  zh: {
    // Brand
    brand: "RevenuePilot",
    pageTitle: "RevenuePilot OS",
    headerTitle: "一人公司创业控制台",

    // Nav
    nav_dashboard: "仪表盘",
    nav_skills: "技能",
    nav_workflows: "工作流",
    nav_history: "历史",
    nav_settings: "设置",

    // Sidebar info
    user: "用户",
    project: "项目",
    api: "API",
    sameOrigin: "同源",

    // Header status
    authenticated: "已认证",
    noApiKey: "未设置 API Key",

    // Language toggle
    langToggle: "EN",

    // Dashboard
    loadingDashboard: "正在加载仪表盘…",
    failedDashboard: "加载仪表盘失败",
    serviceHealth: "服务健康状态",
    database: "数据库",
    skillRuns: "技能运行次数",
    workflowRuns: "工作流运行次数",
    metrics: "指标",
    unknown: "未知",

    // Skills
    skill: "技能",
    selectSkill: "选择技能",
    inputPayload: "输入参数 (JSON)",
    skillInputPayload: "技能输入参数",
    running: "运行中…",
    runSkill: "运行技能",
    result: "结果",
    failedSkills: "加载技能失败",

    // Workflows
    ideaToOffer: "从创意到报价",
    dealToDelivery: "从成交到交付",
    contentToProduct: "内容转产品",
    ideaToOfferDesc: "诊断创始人画像、选择细分市场、验证市场需求，并打造产品化报价。",
    dealToDeliveryDesc: "辅导 CRM 商机、撰写提案，并规划交付项目。",
    contentToProductDesc: "将知识资产转化为产品化报价。",
    workflowInputPayload: "工作流输入参数 (JSON)",
    runWorkflow: "运行工作流",

    // History
    loadingHistory: "正在加载历史记录…",
    failedHistory: "加载历史记录失败",
    runs: "运行记录",
    refreshHistory: "刷新历史记录",
    noRunsYet: "暂无运行记录。",
    details: "详情",
    selectRunToView: "选择一条运行记录查看详情。",

    // Settings
    apiBaseUrl: "API 基础地址",
    apiBaseUrlPlaceholder: "留空则使用同源地址",
    apiBaseUrlHint: "本地开发使用 Vite 代理时留空。远程后端请填写完整 URL。",
    userId: "用户 ID",
    userIdHint: "生产环境下需作为 X-User-Id 请求头发送。",
    apiKey: "API Key",
    apiKeyHint: "生产环境下需作为 X-API-Key 请求头发送。",
    defaultProjectId: "默认项目 ID",
    saveSettings: "保存设置",
    settingsSaved: "设置已保存。",
    testConnection: "测试连接",
    connectionOk: "连接验证成功。",
    connectionFailed: "连接失败",
    showApiKey: "显示 API Key",
    hideApiKey: "隐藏 API Key",

    // Business nav
    nav_projects: "项目",
    nav_ideas: "创意",
    nav_personas: "用户画像",
    nav_offers: "报价",
    nav_landing_pages: "落地页",
    nav_outreach: "外联",
    nav_leads: "线索",
    nav_deals: "商机",
    nav_proposals: "提案",
    nav_delivery: "交付",
    nav_revenue: "收入",
    nav_business_dashboard: "总览",

    // Common CRUD
    loading: "加载中…",
    create: "创建",
    update: "更新",
    delete: "删除",
    save: "保存",
    cancel: "取消",
    edit: "编辑",
    confirmDelete: "确定要删除此项吗？",
    noData: "暂无数据。",
    name: "名称",
    status: "状态",
    actions: "操作",
    data: "数据",
    created: "创建时间",
    updated: "更新时间",
    selectProjectFirst: "请先在项目页或设置中选择一个项目。",
    errorOccurred: "发生错误",

    // Projects
    projectsTitle: "项目",
    projectName: "项目名称",
    projectNamePlaceholder: "我的一人公司项目",
    projectDescription: "描述",
    createProject: "创建项目",
    noProjects: "暂无项目，创建一个开始吧。",
    useProject: "设为当前项目",
    currentProject: "当前",
    projectSelected: "当前项目已更新。",

    // Ideas
    ideasTitle: "创意",
    generateIdeas: "生成创意",
    convertToOffer: "转为报价",
    ideaTitle: "标题",
    ideaSummary: "摘要",
    noIdeas: "暂无创意，用 AI 生成一些吧！",

    // Personas
    personasTitle: "用户画像",
    generatePersona: "生成画像",
    generateInterview: "生成访谈",
    personaName: "画像名称",
    personaRole: "角色",
    personaBusinessType: "业务类型",
    personaDemographics: "人口统计",
    personaPains: "痛点",
    noPersonas: "暂无画像，用 AI 生成一个吧！",

    // Offers
    offersTitle: "报价",
    generateLandingPage: "生成落地页",
    generateOutreachKit: "生成外联工具包",
    offerName: "报价名称",
    offerPrice: "价格",
    offerTargetCustomer: "目标客户",
    offerDescription: "描述",
    noOffers: "暂无报价，从创意转换或手动创建吧！",

    // Landing Pages
    landingPagesTitle: "落地页",
    publish: "发布",
    unpublish: "下架",
    landingPageTitle: "页面标题",
    landingPageStatus: "状态",
    landingPageUrl: "链接",
    noLandingPages: "暂无落地页。",

    // Outreach
    outreachTitle: "外联资产",
    approveOutreach: "批准",
    outreachChannel: "渠道",
    outreachSubject: "主题",
    outreachStatus: "状态",
    noOutreach: "暂无外联资产。",

    // Leads
    leadsTitle: "线索",
    leadName: "线索名称",
    leadSource: "来源",
    leadStatus: "状态",
    noLeads: "暂无线索。",

    // Deals
    dealsTitle: "商机",
    markWon: "标记赢单",
    markLost: "标记输单",
    generateProposal: "生成提案",
    generateDeliveryProject: "生成交付项目",
    dealTitle: "商机标题",
    dealValue: "金额",
    dealStage: "阶段",
    noDeals: "暂无商机。",

    // Proposals
    proposalsTitle: "提案",
    proposalTitle: "提案标题",
    proposalStatus: "状态",
    noProposals: "暂无提案。",

    // Delivery
    deliveryTitle: "交付项目",
    deliveryProjectTitle: "项目标题",
    deliveryStatus: "状态",
    deliveryTasks: "任务",
    addTask: "添加任务",
    taskTitle: "任务标题",
    taskStatus: "任务状态",
    noDeliveryProjects: "暂无交付项目。",
    noTasks: "暂无任务。",

    // Revenue
    revenueTitle: "收入记录",
    revenueAmount: "金额",
    revenueSource: "来源",
    revenueDate: "日期",
    totalRevenue: "总收入",
    noRevenue: "暂无收入记录。",

    // Business Dashboard
    overviewTitle: "业务总览",
    totalRevenueLabel: "总收入",
    activeLeads: "活跃线索",
    openDeals: "进行中商机",
    activeOffers: "活跃报价",
    openDelivery: "进行中交付",
    nextActions: "下一步行动",
    noNextActions: "全部搞定！暂无待办事项。",

    // Error boundary
    errorTitle: "出错了",
    errorBody: "控制台遇到意外错误。你的数据是安全的——重新加载通常即可恢复。",
    errorDetails: "技术细节",
    errorReload: "重新加载控制台",
    close: "关闭",
  },
} as const;

export type TranslationKey = keyof typeof translations.en;
