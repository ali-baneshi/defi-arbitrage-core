# راهنمای پیشرفته زیرساخت

## فلسفه طراحی

این پروژه زیرساخت‌محور طراحی شده است. ارزش آن در کوچک‌بودن، قطعی‌بودن و قابل‌فهم‌بودن زیر review است. هر boundary اصلی سعی می‌کند به یک سؤال عملی پاسخ دهد: چه چیزی قابل اعتماد است، چه چیزی باید validation شود و چه چیزی باید بیرون از این package بماند.

نتیجه، سیستمی است که نسبت به repositoryهای monolithic آربیتراژ که تحلیل، execution، wallet، قرارداد، deployment و عملیات را با هم مخلوط می‌کنند، audit و توسعه و embedding ساده‌تری دارد.

## مرزهای سیستم

هسته، snapshot محلی را می‌گیرد و report محلی برمی‌گرداند. این boundary کاملاً عمدی است.

داخل این boundary، تمرکز روی contractهای قطعی، تحلیل graph، policy filtering و معناشناسی پایدار خروجی است. بیرون از این boundary، adopterها آزادند که collector، pricing service، decision engine، transaction system یا deployment workflow خودشان را با کنترل‌های مناسب بسازند.

به همین دلیل این repository می‌تواند هم زیرساخت مشترک داخل یک شرکت باشد و هم پایه‌ای عمومی برای ابزارهای متن‌باز دیگر.

## مدل اعتماد

providerها و acceleratorهای اختیاری به‌عنوان boundary غیرقابل‌اعتماد در نظر گرفته می‌شوند. یک provider ممکن است فایل خراب یا داده ناسازگار بخواند. یک accelerator ممکن است fail شود، diverge کند یا در دسترس نباشد. بنابراین سیستم ورودی‌ها را صریح validation می‌کند و مسیر Python را حفظ می‌کند تا حتی در نبود Rust، رفتار authoritative باقی بماند.

این مدل اعتماد برای سازمان‌هایی مفید است که به failure mode قابل پیش‌بینی نیاز دارند، نه فرض‌های خوش‌بینانه.

## مدل توسعه‌پذیری

این سیستم برای توسعه توسط افراد، startupها، تیم‌های platform داخلی و شرکت‌های بزرگ طراحی شده است.

الگوی رایج توسعه این است که:

- contract snapshot پایدار بماند
- providerهای جدید برای datasetهای عمومی یا اختصاصی اضافه شوند
- exampleهای شبکه‌ای و testهای منفی بیشتر اضافه شوند
- reporter یا wrapper سفارشی برای dashboard، queue یا notebook داخلی ساخته شود
- execution، custody و network production در serviceهای جدا باقی بمانند

این الگو اجازه می‌دهد چند تیم از یک analysis kernel مشترک استفاده کنند، بدون اینکه مجبور باشند معماری عملیاتی یکسانی داشته باشند.

## کاربردهای سازمانی مناسب

برای یک researcher فردی، این پروژه پایه‌ای تمیزتر از scriptهای پراکنده فراهم می‌کند.

برای یک تیم trading یا market-structure، می‌تواند مرحله تحلیل قطعی درون یک pipeline بزرگ‌تر review فرصت باشد.

برای یک شرکت protocol یا infrastructure، می‌تواند لایه reusable برای validation و route analysis در serviceهای داخلی، محیط‌های simulation یا tooling شریک‌ها باشد.

برای engineering manager یا reviewer، artifactها، schemaها و boundaryهای روشن باعث می‌شوند ارزیابی فنی سریع‌تر انجام شود.

## معیار کیفیت برای استفاده عمومی

یک repository زیرساختی عمومی باید قبل از هر چیز قابل‌فهم باشد. یعنی naming سازگار، exampleهای واقع‌گرایانه، خروجی‌های machine-readable پایدار، زبان صادقانه درباره maturity و blockerهای مشخص برای release داشته باشد.

این repository تلاش می‌کند این معیار را با تمرکز بر این موارد برآورده کند:

- interfaceهای contract-driven
- validation قطعی
- reuse چندشبکه‌ای
- behavior محدود و testable
- evidence روشن برای readiness

## adoption سالم باید چگونه باشد

adoption سالم این repository را به‌عنوان یک bot جادویی نمی‌بیند؛ آن را یک kernel می‌بیند.

تیم‌ها باید contractها را درک کنند، snapshotهای خود را validation کنند، failure modeها را review کنند و سپس سیستم‌های اطراف موردنیازشان را بسازند. در این حالت، repository به پایه‌ای قوی برای research platformها، analytics productها، tooling داخلی توسعه‌دهندگان و pipelineهای execution کنترل‌شده تبدیل می‌شود.

## عمیق‌تر: مرزهای زیرساخت

### مرز ورودی

سیستم snapshotهای JSON محلی را که با schema مستند شده مطابقت دارند، می‌پذیرد. این مرز صریح و validation‌شده است:

- **Schema Validation**: هر snapshot قبل از پردازش با `schemas/market_snapshot.schema.json` بررسی می‌شود
- **Business Rule Validation**: هویت network، سلامت edge، محدوده liquidity و معقول‌بودن fee اجباری است
- **Fail-Closed Semantics**: ورودی نامعتبر زود و با پیام خطای ساخت‌یافته رد می‌شود، هرگز بی‌صدا نادیده گرفته نمی‌شود
- **No Network Assumptions**: سیستم هرگز داده fetch نمی‌کند، هرگز RPC در دسترس فرض نمی‌کند، هرگز API key نمی‌خواهد

این طراحی یعنی می‌توانید کل pipeline تحلیل را با فایل‌های fixture، snapshotهای version-controlled یا شرایط بازار تولیدشده مصنوعی بدون وابستگی خارجی تست کنید.

### مرز پردازش

داخل مرز، سیستم روی تحلیل قطعی graph تمرکز دارد:

- **Cycle Detection**: شمارش چرخه محدود مبتنی بر Bellman-Ford با محدودیت عمق قابل تنظیم
- **Rate Composition**: محاسبه ضربی rate با کسر صریح fee در هر hop
- **Liquidity Constraints**: تخمین ظرفیت بر اساس liquidity محدودکننده در هر مسیر
- **Policy Filtering**: آستانه حداقل سود قابل تنظیم، حداکثر طول مسیر و قوانین خاص شبکه

engine طراحی شده تا برای ورودی یکسان، خروجی یکسان تولید کند، صرف‌نظر از محیط اجرا، timestamp یا وضعیت سیستم. این قطعیت برای research قابل تکرار، regression testing و deployment چندمحیطی حیاتی است.

### مرز خروجی

سیستم خروجی ساخت‌یافته و پایدار در دو فرمت تولید می‌کند:

- **Human-Readable Text**: جداول فرمت‌شده با network، path، venues، profit basis points و capacity
- **Machine-Readable JSON**: اشیاء opportunity ساخت‌یافته مطابق با `schemas/opportunity_report.schema.json`

پایداری خروجی از طریق این موارد اجباری می‌شود:

- **Schema Contracts**: شکل خروجی JSON مستند و در CI validation می‌شود
- **Deterministic Ordering**: opportunityها بر اساس سود نزولی، سپس طول مسیر مرتب می‌شوند
- **Stable Field Names**: تغییرات breaking در ساختار خروجی نیاز به major version bump دارند
- **Diagnostics Separation**: خطاها، هشدارها و metadata به stderr یا کانال‌های diagnostic جداگانه فرستاده می‌شوند

این باعث می‌شود سیستم برای embedding در pipelineهای خودکار، dashboardها و سیستم‌های تصمیم downstream امن باشد.

### مرز توسعه

سیستم برای توسعه بدون تغییر طراحی شده:

- **Provider Protocol**: `SnapshotProvider` را پیاده‌سازی کنید تا منابع داده اختصاصی را نرمال کنید
- **Reporter Protocol**: `OpportunityReporter` را پیاده‌سازی کنید تا فرمت‌های سفارشی (CSV، Parquet، نوشتن database) تولید کنید
- **Policy Protocol**: `OpportunityPolicy` را پیاده‌سازی کنید تا منطق filtering خاص domain اضافه کنید
- **Service Protocol**: `AnalysisService` را پیاده‌سازی کنید تا engineهای تحلیل جایگزین (Rust، C++، GPU-accelerated) یکپارچه کنید

extensionها پشت interfaceهای پایدار ایزوله شده‌اند و به تیم‌ها اجازه می‌دهند رفتار را بدون fork کردن engine اصلی سفارشی کنند.

## عمیق‌تر: مدل اعتماد

### ورودی غیرقابل‌اعتماد

تمام داده‌های خارجی غیرقابل‌اعتماد در نظر گرفته می‌شوند:

- **File Providers**: ممکن است JSON خراب، UTF-8 نامعتبر یا فایل‌هایی با payloadهای حمله embedded بخوانند
- **Custom Providers**: ممکن است داده ناسازگار برگردانند، contractهای schema را نقض کنند یا تعریف edgeهای مخرب inject کنند
- **Environment Variables**: ممکن است مقادیر غیرمنتظره، تلاش‌های injection یا مسیرهای پیکربندی‌شده اشتباه داشته باشند

لایه validation مرز اعتماد است. هیچ چیز بدون عبور از schema validation، بررسی business rule و محدوده sanity وارد engine نمی‌شود.

### acceleratorهای غیرقابل‌اعتماد

تحلیل اختیاری Rust به‌عنوان accelerator غیرقابل‌اعتماد در نظر گرفته می‌شود:

- **Process Isolation**: باینری Rust در یک process جداگانه بدون shared memory اجرا می‌شود
- **Timeout Protection**: processهای Rust طولانی‌مدت بعد از timeout قابل تنظیم kill می‌شوند
- **Fallback Semantics**: اگر Rust fail شود، diverge کند یا در دسترس نباشد، تحلیل Python authoritative باقی می‌ماند
- **Parity Validation**: test suite تأیید می‌کند که Rust و Python روی snapshotهای مرجع نتایج یکسان تولید می‌کنند

این طراحی به تیم‌ها اجازه می‌دهد از performance Rust بهره ببرند بدون ایجاد وابستگی سخت یا single point of failure.

### هسته قابل‌اعتماد

پیاده‌سازی Python زیر `src/arbcore/` هسته قابل‌اعتماد است:

- **Canonical Semantics**: Python رفتار authoritative برای validation، تحلیل و خروجی تعریف می‌کند
- **Minimal Dependencies**: تحلیل اصلی فقط به کتابخانه استاندارد Python نیاز دارد
- **Auditable Size**: engine اصلی زیر 2000 خط Python است، برای review انسانی طراحی شده
- **Deterministic Behavior**: بدون تصادفی‌بودن، بدون timestamp در خروجی، بدون منطق وابسته به محیط

این مدل اعتماد سیستم را برای محیط‌های حساس به امنیت که وابستگی‌های خارجی و رفتار غیرقطعی غیرقابل‌قبول است، مناسب می‌کند.

## عمیق‌تر: معماری چندشبکه‌ای

### Network به‌عنوان مفهوم درجه یک

فیلد `network` در هر snapshot اجباری و صریح است:

```json
{
  "network": "base",
  "timestamp": "2026-05-07T00:00:00Z",
  "edges": [...]
}
```

این طراحی مزایای متعددی دارد:

- **No Implicit Assumptions**: engine هرگز حدس نمی‌زند snapshot کدام شبکه را نمایندگی می‌کند
- **Multi-Network Pipelines**: یک analysis service می‌تواند snapshotها از Ethereum، Base، Arbitrum، Polygon و غیره را پردازش کند
- **Network-Specific Policies**: شبکه‌های مختلف می‌توانند آستانه سود، فرض‌های gas یا فیلترهای liquidity متفاوت داشته باشند
- **Audit Trail**: هر opportunity report شبکه منبع را شامل می‌شود و تحلیل را قابل ردیابی می‌کند

### Engine بی‌طرف نسبت به شبکه

engine اصلی عمداً بی‌طرف نسبت به شبکه است:

- **No Hardcoded Chains**: بدون case خاص برای Ethereum در مقابل Base در مقابل Arbitrum
- **No RPC Assumptions**: بدون دانش از block time، gas price یا مکانیزم‌های consensus
- **No Token Registries**: بدون آدرس token یا mapping symbol hardcoded
- **No Venue Catalogs**: بدون فرض درباره اینکه کدام DEXها روی کدام شبکه‌ها وجود دارند

این engine را قابل استفاده مجدد در این موارد می‌کند:

- **Public Mainnets**: Ethereum، Base، Arbitrum، Optimism، Polygon، Avalanche، BNB Chain
- **Public Testnets**: Sepolia، Goerli، Base Sepolia، Arbitrum Sepolia
- **Private Networks**: testnetهای داخلی، محیط‌های forked، شبکه‌های simulation
- **Future Networks**: هر chain سازگار با EVM بدون تغییر کد

### extensionهای خاص شبکه

تیم‌ها می‌توانند منطق خاص شبکه را از طریق extension pointها اضافه کنند:

- **Custom Providers**: منابع داده خاص شبکه را نرمال کنید (Uniswap V3 روی Ethereum، Aerodrome روی Base)
- **Custom Policies**: فیلترهای خاص شبکه اعمال کنید (آستانه سود بالاتر روی شبکه‌های گران)
- **Custom Reporters**: metadata خاص شبکه تولید کنید (تخمین gas، تأییدیه block)

این جداسازی هسته را تمیز نگه می‌دارد در حالی که سفارشی‌سازی عملی را امکان‌پذیر می‌کند.

## عمیق‌تر: Validation به‌عنوان زیرساخت

### چرا Validation مهم است

در سیستم‌های production، شکست‌های بی‌صدا خطرناک‌تر از شکست‌های بلند هستند. این repository validation را به‌عنوان یک ویژگی درجه یک در نظر می‌گیرد:

- **Early Detection**: ورودی نامعتبر قبل از شروع تحلیل رد می‌شود، نه بعد از پردازش جزئی
- **Structured Errors**: شکست‌های validation اشیاء خطای machine-readable با مسیرهای field و توضیحات نقض تولید می‌کنند
- **Fail-Closed**: سیستم از پردازش ورودی مبهم یا ناامن امتناع می‌کند، هرگز به رفتار "بهترین حدس" fallback نمی‌کند
- **Audit Trail**: نتایج validation لاگ می‌شوند و می‌توانند برای compliance review ذخیره شوند

### Validation سطح Schema

schemaهای JSON زیر `schemas/` contractهای عمومی را مستند می‌کنند:

- **market_snapshot.schema.json**: شکل snapshotهای ورودی را تعریف می‌کند
- **opportunity_report.schema.json**: شکل opportunityهای خروجی را تعریف می‌کند
- **diagnostics.schema.json**: شکل diagnostics سیستم را تعریف می‌کند
- **error_response.schema.json**: شکل خطاهای ساخت‌یافته را تعریف می‌کند

این schemaها اهداف متعددی دارند:

- **Documentation**: توسعه‌دهندگان می‌توانند schema را بخوانند تا ورودی/خروجی مورد انتظار را بفهمند
- **Validation**: بررسی‌های runtime انطباق schema را اجباری می‌کنند
- **Code Generation**: تیم‌ها می‌توانند کتابخانه‌های client از schemaها تولید کنند
- **Contract Testing**: CI تأیید می‌کند که خروجی واقعی با contractهای schema مطابقت دارد

### Validation Runtime

فراتر از schema validation، سیستم business ruleها را اجباری می‌کند:

- **Network Identity**: فیلد `network` باید موجود و غیرخالی باشد
- **Edge Sanity**: rateها باید مثبت، feeها باید غیرمنفی، liquidity باید مثبت باشد
- **Symbol Consistency**: edgeها باید مسیرهای معتبر تشکیل دهند (target edge N باید با source edge N+1 مطابقت کند)
- **Bounded Complexity**: snapshotها نمی‌توانند از حداکثر تعداد edge تجاوز کنند (از DoS از طریق graphهای عظیم جلوگیری می‌کند)

این بررسی‌ها در برابر این موارد محافظت می‌کنند:

- **Data Quality Issues**: snapshotهای خراب، داده قدیمی، نرمال‌سازی ناسازگار
- **Attack Vectors**: snapshotهای مخرب طراحی‌شده برای ایجاد crash، حلقه بی‌نهایت یا exhaustion منابع
- **Integration Bugs**: سیستم‌های upstream که به دلیل تغییرات کد contractها را نقض می‌کنند

### Validation Case منفی

repository شامل caseهای تست منفی صریح است:

- **Missing Required Fields**: snapshotها بدون `network` یا `edges` باید رد شوند
- **Invalid Data Types**: rateهای string، liquidity منفی، edgeهای غیرآرایه باید رد شوند
- **Business Rule Violations**: edgeهای zero-rate، self-loop، graphهای disconnected باید رد شوند

این تست‌ها ثابت می‌کنند که سیستم وقتی ورودی بد می‌گیرد، به‌طور امن و قابل پیش‌بینی fail می‌شود.

## نتیجه‌گیری: زیرساخت، نه محصول

این repository زیرساخت است، نه محصول. یک kernel است، نه یک سیستم کامل. یک پایه است، نه یک ساختمان تمام‌شده.

تیم‌هایی که با موفقیت آن را adopt می‌کنند این تمایز را درک می‌کنند. آن را به‌عنوان یک لایه تحلیل تمیز، قابل audit و قطعی درون یک سیستم بزرگ‌تر که کنترل می‌کنند استفاده می‌کنند. جمع‌آوری داده خودشان، مدیریت ریسک خودشان، منطق execution خودشان و شیوه‌های عملیاتی خودشان را اضافه می‌کنند.

تیم‌هایی که با آن مشکل دارند آن را به‌عنوان یک bot جادویی که باید out of the box کار کند در نظر می‌گیرند. انتظار دارند داده جمع کند، walletها را مدیریت کند، معاملات را اجرا کند و بدون مهندسی اضافی سود تولید کند.

repository برای گروه اول طراحی شده است. اگر در گروه دوم هستید، این ابزار مناسب شما نیست.

اگر در گروه اول هستید، خوش آمدید. contractها را بخوانید، snapshotهای خود را validation کنید، failure modeها را review کنید و چیز عالی‌ای روی این پایه بسازید.
