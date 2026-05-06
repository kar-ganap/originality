# Phase 1.2 H2 hand audit — sheet

Generated: 100 papers from `section0-sample-1M-v2.parquet`, stratified 50 uniform + 50 pre-1990. Audit seed: `ws2-phase-1.2-h2-audit-seed-v1`.

## Reviewer task

For each of the 100 papers below, decide whether §0 was right to include it. Write one verdict on the `**Verdict:** _____` line:

- **`OK`** — clearly a research paper in cs or physics with a real abstract. No further note needed.
- **`FLAG: WRONG_FIELD`** — paper is primarily about something else (e.g., chemistry, marketing, biology) and only got tagged as cs/physics because of one or two boilerplate keywords. Add a short reason.
- **`FLAG: BAD_ABSTRACT`** — the abstract is publisher boilerplate (citation menu, icon labels, download buttons), OCR fragments, a stub like "Abstract not available," or otherwise unusable as a representation of the paper's content.
- **`FLAG: JUNK_YEAR`** — pre-1990 paper that contains a post-2000 token the regex missed (e.g., "ChatGPT", "blockchain", "transformer architecture"). Note the specific token.
- **`FLAG: BORDERLINE`** — you're not sure; note why.

**Three things to know going in:**

1. The pass criterion of "0 FLAGs" is aspirational. We expect some FLAGs — the goal is to characterize which patterns of §0 false positives are common, not to certify perfection.
2. Multi-field papers (e.g., a real cs paper that also has bio concepts) are **OK**. The test is whether the paper genuinely belongs in a cs/physics analytical population, not whether cs/physics is its only or primary field.
3. If you start seeing the same FLAG pattern repeat (3+ instances of the same root cause), you can stop reviewing the rest of that pattern's likely cases and just note "pattern X seen ≥3 times; recommend filter Y." We're after kinds of error, not a complete enumeration.

---

##   1. [W2233482070](https://openalex.org/W2233482070) — 2008 — article — `uniform`

**Concepts:** Spurious relationship (0.71), Continuous variable (0.62), Variables (0.58), Variable (mathematics) (0.50), Principal (computer security) (0.45)

**Title:** Death to Dichotomizing: Figure 1

> Why call for a death to dichotomizing? The Journal of Consumer Research receives manuscripts on an almost daily basis in which researchers have dichotomized (often referred to as median splitting) a continuous independent variable. There are two principal problems with this approach to data analysis, each of which is very well documented in the literature. The first is that by dichotomizing continuous independent variables researchers are quite likely reducing the statistical power available to test their hypotheses (Irwin and McClelland 2003). The second, potentially more troubling, problem is that inappropriate dichotomizing of continuous data can at times create spurious significant results if the independent variables are correlated (Maxwell and Delaney 1993). And yet, despite these well-known problems, dichotomizing is an extremely frequent activity for experimental consumer researchers. The goal of this editorial is not to write an in-depth methodological piece on this subject but rather to briefly outline why all consumer researchers should be concerned about this topic. I also hope to illustrate how we can easily write up appropriately conducted analyses when our research designs include continuous independent variables. (For more thorough, methodological pieces on this topic I suggest an excellent and concise article in the Journal of Marketing Research [Irwin and McClelland 2001] or a truly comprehensive guide to performing analysis including continuous independent variables and interactions [Aiken and West 1991].)

Likely the most common research design utilized by experimental consumer researchers is a very straightforward manipulation of one or more independent variables that the researcher believes will affect a dependent variable. Virtually all consumer researchers learn at one point how to describe and analyze such designs and are typically quite adept at it. For example, a researcher manipulates two independent variables between subjects and performs a two-by-two ANOVA examining their impact on a dependent variable …

**Verdict:** _____

---

##   2. [W2951693171](https://openalex.org/W2951693171) — 2014 — preprint — `uniform`

**Concepts:** Pairing (0.87), Condensed matter physics (0.80), Fermi surface (0.77), Physics (0.74), Cuprate (0.71)

**Title:** "Nodal gap" induced by the incommensurate diagonal spin density modulation in underdoped high-$T_c$ superconductors

> Recently it was revealed that the whole Fermi surface is fully gapped for several families of underdoped cuprates. The existence of the finite energy gap along the $d$-wave nodal lines ("nodal gap") contrasts the common understanding of the $d$-wave pairing symmetry, which challenges the present theories for the high-$T_c$ superconductors. Here we propose that the incommensurate diagonal spin-density-wave order can account for the above experimental observation. The Fermi surface and the local density of states are also studied. Our results are in good agreement with many important experiments in high-$T_c$ superconductors.

**Verdict:** _____

---

##   3. [W2105804376](https://openalex.org/W2105804376) — 1966 — article — `uniform`

**Concepts:** Icon (0.85), Citation (0.72), Download (0.57), Information retrieval (0.49), Computer science (0.48)

**Title:** Heat-Release Profiles in the High-Temperature Oxidation of Acetylene in Shock Waves

> Views Icon Views Article contents Figures & tables Video Audio Supplementary Data Peer Review Share Icon Share Twitter Facebook Reddit LinkedIn Tools Icon Tools Reprints and Permissions Cite Icon Cite Search Site Citation W. C. Gardiner, W. G. Mallard, K. Morinaga, D. L. Ripley, B. F. Walker; Heat‐Release Profiles in the High‐Temperature Oxidation of Acetylene in Shock Waves. J. Chem. Phys. 15 June 1966; 44 (12): 4653–4654. https://doi.org/10.1063/1.1726700 Download citation file: Ris (Zotero) Reference Manager EasyBib Bookends Mendeley Papers EndNote RefWorks BibTex toolbar search Search Dropdown Menu toolbar search search input Search input auto suggest filter your search All ContentAIP Publishing PortfolioThe Journal of Chemical Physics Search Advanced Search |Citation Search

**Verdict:** _____

---

##   4. [W2030174386](https://openalex.org/W2030174386) — 1984 — article — `uniform`

**Concepts:** Computer science (0.78), Access method (0.56), Index (typography) (0.52), Public access (0.51), Primary (astronomy) (0.50)

**Title:** KSAM

> This paper reports research undertaken to design and implement a B+-tree-based keyed sequential-access method (KSAM). KSAM provides primary and secondary access, which can be based on direct or sequential processing. Primary access to a data file requires three levels of indexes: super, master, and primary indexes. Secondary access requires an additional index level: secondary indexes. The superindex and master indexes are transparent to the user and are used solely by the system.

**Verdict:** _____

---

##   5. [W7132538725](https://openalex.org/W7132538725) — 2025 — dissertation — `uniform`

**Concepts:** Physics (0.62), Humanities (0.42), Theology (0.34), Engineering (0.33), Computer science (0.31)

**Title:** Urban Waterfront Revitalization of Grčevo, Integrating 3D Technologies and Sustainable Solutions

> Obale gradova definirane su kao prijelazne zone između urbanog tkiva i vode. One se često smatraju pokretačima urbanog razvoja jer njihovo uređenje ima potencijal stvoriti novu sliku grada, privući investicije i spriječiti propadanje prostora. Ovaj rad predlaže cjelovito uređenje obale na području Grčeva, na potezu od brodogradilišta Viktor Lenac do lučice Borik. Projekt obuhvaća izgradnju suvremene obalne šetnice, uređenje plažnih prostora i formiranje žala, kao i stvaranje uvjeta za smještaj suhe marine (suhe komunalne luke) namijenjene plovilima, čime se prostor obogaćuje dodatnim sadržajima javne i rekreativne namjene. Cilj je revitalizirati sada zapušten i infrastrukturno nedovoljno razvijen dio obale, stvarajući pritom funkcionalan, siguran i krajobrazno privlačan javni prostor. Primarni naglasak stavljen je na projektiranje šetnice, dok su za ostale objekte dane okvirne dimenzije, preliminarna situacija i lokacija izgradnje. Metodološki okvir rada temelji se na primjeni suvremenih tehnologija snimanja i digitalne dokumentacije prostora. Korištenjem LiDAR-a, ručnog LiDAR-a te 3D oblaka točaka, uz primjenu SLAM HLS tehnologije, provodi se precizno trodimenzionalno mapiranje obalnog pojasa. Tako prikupljeni podaci omogućuju detaljnu analizu topografskih, infrastrukturnih i prirodnih elemenata te služe kao podloga za planiranje optimalnih rješenja.

**Verdict:** _____

---

##   6. [W4404619172](https://openalex.org/W4404619172) — 2024 — article — `uniform`

**Concepts:** Gynecology (0.52), Physics (0.44), Philosophy (0.33), Medicine (0.25)

**Title:** ÇİN-JAPONYA İLİŞKİLERİNDE ULUSLARARASI SİSTEM KAYNAKLI DEĞİŞİMLER: TEHDİT DENGESİ TEORİSİ BAĞLAMINDA BİR DEĞERLENDİRME

> Bu çalışma, on dokuzuncu yüzyılın sonlarında belirgin şekilde uluslararası sisteme eklemlenen Japonya ve Çin’in, bu tarihlerden günümüze kadar olan dönemdeki ikili ilişkilerini ve bu ilişkilerin uluslararası sistemin etkisiyle uğradığı değişimleri “Tehdit Dengesi Teorisi” bağlamında açıklamayı amaçlamaktadır. Çalışmada Japonya ve Çin ilişkilerinin tarihi, sistem düzeyinde ve sistem dönemlerine göre değerlendirilmiştir. İki ülkenin on dokuzuncu yüzyılın sonlarından günümüze kadar sırasıyla çok kutuplu, çift kutuplu ve son olarak tek kutuplu veya gevşek tek kutuplu sistemlerdeki ilişkilerinin değişimleri anlatılmış ve bu şekilde dönemsel olarak ortaya çıkan farklılıklar açıklanmaya çalışılmıştır. İki ülke arasında ortaya çıkan bu farklılıkların sebebi realist teori kapsamında Stephen Walt’un öne sürdüğü Tehdit Dengesi Teorisi ile tespit edilmeye çalışılmıştır. Çalışmada, tehdit algılarının değişiminin değerlendirilmesi ve tespiti de Tehdit Dengesi Teorisi kapsamında öne sürülen dört değerlendirme birimine göre yapılmıştır. Bu bağlamda çalışmada ilk olarak, Tehdit Dengesi Teorisi ve değerlendirme birimleri açıklanmıştır. Ardından, günümüze değin Çin-Japonya ilişkileri gözden geçirilmiş ve iki ülke arasındaki temel sorunlar açıklanmıştır. Son olarak, on dokuzuncu yüzyılın sonlarından günümüze kadar geçen sürede meydana gelen sistem değişikliklerinin iki ülke ilişkileri üzerine yansımaları dört değerlendirme birimi temelinde ve tehdit algısı bağlamında değerlendirilmiştir. Varılan sonuca göre, geleneksel rakipler olarak kendileri için birbirlerinden daha büyük tehlikeler hissettikleri dönemlerde Çin ve Japonya daha iyi ilişkilere sahip olmuşlardır. Uluslararası sistemin yapısında kaynaklı olarak kendilerine yönelmiş daha büyük tehditler görmediklerinde ise iki ülke daha sorunlu ve çatışmacı dönemler geçirme başlamışlardır.

**Verdict:** _____

---

##   7. [W2041442090](https://openalex.org/W2041442090) — 1982 — article — `uniform`

**Concepts:** Algorithm (0.63), Type (biology) (0.46), Artificial intelligence (0.45), Computer science (0.36), Geology (0.13)

**Title:** A Tauberian theorem for strong Abel summability type

> In the present paper the author has defined a new method of strong Abel summability type <inline-formula content-type="math/mathml"> <mml:math xmlns:mml="http://www.w3.org/1998/Math/MathML" alttext="left-brace upper A comma lamda right-brace Subscript m"> <mml:semantics> <mml:mrow class="MJX-TeXAtom-ORD"> <mml:mo fence="false" stretchy="false">{</mml:mo> <mml:mi>A</mml:mi> <mml:mo>,</mml:mo> <mml:mi>λ</mml:mi> <mml:msub> <mml:mo fence="false" stretchy="false">}</mml:mo> <mml:mi>m</mml:mi> </mml:msub> </mml:mrow> <mml:annotation encoding="application/x-tex">{\{ A,\lambda \} _m}</mml:annotation> </mml:semantics> </mml:math> </inline-formula> and obtained a necessary and sufficient type of Tauberian conditions for <inline-formula content-type="math/mathml"> <mml:math xmlns:mml="http://www.w3.org/1998/Math/MathML" alttext="normal upper Sigma a Subscript n"> <mml:semantics> <mml:mrow> <mml:mi mathvariant="normal">Σ</mml:mi> <mml:mrow class="MJX-TeXAtom-ORD"> <mml:msub> <mml:mi>a</mml:mi> <mml:mi>n</mml:mi> </mml:msub> </mml:mrow> </mml:mrow> <mml:annotation encoding="application/x-tex">\Sigma {a_n}</mml:annotation> </mml:semantics> </mml:math> </inline-formula> to be summable <inline-formula content-type="math/mathml"> <mml:math xmlns:mml="http://www.w3.org/1998/Math/MathML" alttext="left-bracket upper R comma lamda comma k right-bracket Subscript m"> <mml:semantics> <mml:mrow class="MJX-TeXAtom-ORD"> <mml:mo stretchy="false">[</mml:mo> <mml:mi>R</mml:mi> <mml:mo>,</mml:mo> <mml:mi>λ</mml:mi> <mml:mo>,</mml:mo> <mml:mi>k</mml:mi> <mml:msub> <mml:mo stretchy="false">]</mml:mo> <mml:mi>m</mml:mi> </mml:msub> </mml:mrow> <mml:annotation encoding="application/x-tex">{[R,\lambda ,k]_m}</mml:annotation> </mml:semantics> </mml:math> </inline-formula>, whenever it is summable <inline-formula content-type="math/mathml"> <mml:math xmlns:mml="http://www.w3.org/1998/Math/MathML" alttext="left-brace upper A comma lamda right-brace Subscript m"> <mml:semantics> <mml:mrow class="MJX-TeXAtom-ORD"> <mml:mo fence="false" stretchy="false">{</mml:mo> <mml:mi>A</mml:mi> <mml:mo>,</mml:mo> <mml:mi>λ</mml:mi> <mml:msub> <mml:mo fence="false" stretchy="false">}</mml:mo> <mml:mi>m</mml:mi> </mml:msub> </mml:mrow> <mml:annotation encoding="application/x-tex">{\{ A,\lambda \} _m}</mml:annotation> </mml:semantics> </mml:math> </inline-formula>. This result is analogous to one result of Flett [<bold>4</bold>].

**Verdict:** _____

---

##   8. [W4287777920](https://openalex.org/W4287777920) — 2020 — article — `uniform`

**Concepts:** Computer science (0.50)

**Title:** КРИТИЧНІ АСПЕКТИ ПОБУДОВИ ЕКСТЕРНАЛЬНОЇ СИСТЕМИ КОРПОРАТИВНОГО УПРАВЛІННЯ В УКРАЇНІ: ТЕОРЕТИЧНІ ПОЛОЖЕННЯ

> Корпоративне управління є формою організації діяльності корпорації через впорядкований вплив суб’єктів такого управління, їх взаємодію на мікроекономічні процеси, які забезпечують її оптимальне соціоекономічне існування в макроекономічному середовище. Оптимальність соціального і економічного існування відображає рівень досягнення поставлених цілей, мети діяльності корпорації. Не зважаючи не єдність в розумінні значення корпоративного управління, на сьогодні спостерігається чітка диференціація підходів до формування системи управління корпорацією, складу відповідних органів. Очевидним той факт, що в їх основі соціокультурна та економічна специфічність відповідного регіону, що обумовлює індивідуалізацію розвитку макроекономічних ринків.Класичним на сьогоднішньому етапі розвитку суспільства є система екстернального управління (США, Великобританія) передбачає вплив, на розвиток корпорації, отже на модель управління нею, екзогенних економічних факторів, таких, наприклад, як макроекономічні ринки. Індикатором ефективності корпоративного управління виступає рівень капіталізації корпорації на фондовому ринку. В наведеному випадку, акціонерний капітал має низький рівень своєї концентрації з високим рівнем залежності його оборотоздатності від фондового індексу, поточного котирування відповідного фінансового активу. Ефективність корпоративного управління призводить до зміни позитивної динаміки котирування відповідного фінансового активу і навпаки, слабе управління має наслідком зниження вартості активу. Отже фондовий ринок, як основне джерело фінансування, є об’єктивним і саморегулюючим фактором встановлення ефективності корпоративного управління. Висока залежність рівня капіталізації корпорації від зовнішніх факторів, зокрема макроекономічних індикаторів, є свідченням переважаючого характеру спекулятивності руху акціонерного капіталу, отже короткострокові інтереси інвесторів. Наведені умови впливають на формування моделі корпоративного управління.Цей підхід є доволі спрощений та несистемний, а також позбавлений відповідних правових гарантій доброчесності всіх учасників відносин. Безспірно, що в наведений спосіб значно спрощується механізм передачі важелів корпоративного управління юридичною особою. Але, в той же час, відбувається підміна відповідних юридичних категорій.Автором аргументовано, що збереження цілісності полірівневої системи управління корпорацією (скоординоване управління на рівні вищого органу, з управлінням на рівні виконавчого органу корпорації) завдяки можливої трансформації виключно консолідованого комплексу відповідних прав зменшує ризики корпоративного конфлікту між ними, який є одним із тягарів результативності в діяльності корпорації.

**Verdict:** _____

---

##   9. [W2291718387](https://openalex.org/W2291718387) — 2015 — article — `uniform`

**Concepts:** Computer vision (0.87), Artificial intelligence (0.85), Computer science (0.76), Mobile robot (0.73), Segmentation (0.70)

**Title:** A fast object segmentation method for mobile robots based on improved depth information

> Due to the rapid development of mobile robots technology, the object recognition is of great practical significance. The real-time performance and robustness of object segmentation in cluttered environments is a considerable problem in robot vision. In this paper, a new object segmentation method using depth information is presented. Firstly, this approach obtains the object candidate region using the depth clue, then accomplished the depth filtering in the object candidate region. Next, the object region is extended to get the better edge information. Finally, the foreground is extracted and the segmentation results is realized on the color image. This method of object segmentation was tested on a real mobile robot platform and the results of experiments confirmed the excellent performance of the proposed method.

**Verdict:** _____

---

##  10. [W2153116986](https://openalex.org/W2153116986) — 1999 — article — `uniform`

**Concepts:** Computer science (0.76), Computer vision (0.63), Artificial intelligence (0.63), Image registration (0.51), Segmentation (0.49)

**Title:** A minimax entropy registration framework for patient setup verification in radiotherapy

> In external beam radiotherapy (EBRT), patient setup verification over the entire course of fractionated treatment is necessary for accurate delivery of a specified dose to the tumor. We are working on the development of a minimax entropy registration framework for patient setup verification using dual portal images and the treatment planning 3D CT dataset. In this paper, we present an overview of our registration framework, where an iteratively and automatically estimated segmentation of the portal image is utilized to more accurately and robustly register the portal image to the 3D treatment-planning CT data. In addition, we describe initial testing of this approach. We note that, due to low resolution and low contrast of the portal images, this registration presents a difficult problem. We also note that the registration of the images in our proposed method is guided by the bony structure visible in the portal and the 3D CT images. However, since the prostate can move with respect to the pelvic bone, we propose using ultrasound images to quantify this movement.

**Verdict:** _____

---

##  11. [W2368846216](https://openalex.org/W2368846216) — 2006 — article — `uniform`

**Concepts:** Meaning (existential) (0.65), Survey methodology (0.50), Engineering (0.44), Survey research (0.43), Business (0.35)

**Title:** The Survey on Employee Satisfactory Degree(ESD)

> This paper briefly introduces the meaning of the survey on ESD and the important functions of ESD in the sustainable development of the enterprise,and puts forward the procedures and methods of the scientific survey on ESD,and expounds several major factors of guaranteeing the effectiveness of the survey on ESD.

**Verdict:** _____

---

##  12. [W7029699132](https://openalex.org/W7029699132) — 2017 — article — `uniform`

**Concepts:** Listing (finance) (0.67), Linguistics (0.62), Computer science (0.57), Natural language processing (0.45), Artificial intelligence (0.34)

**Title:** LINGUIST List Resources for Musgu

> A page listing all resources on The LINGUIST List website which are relevant to this language or language family.

**Verdict:** _____

---

##  13. [W4292771801](https://openalex.org/W4292771801) — 2019 — article — `uniform`

**Concepts:** Pacific islanders (0.77), Educational leadership (0.44), Medical education (0.37), Computer science (0.34), Psychology (0.33)

**Title:** Exploring Culturally Relevant Leadership Development for Pacific Islander American College Students

> Education research focused on Pacific Islanders over the past 30 years has overwhelmingly concluded that U.S. systems of education are failing these students, but the global movement towards culturally relevant and inclusive education has had an indelible impact on the number and types of support available for Pacific Islander students in the continental United States. The purpose of this project is to explore how culturally relevant leadership development shapes the growth and development of Pacific Islander American college students. We examine quantitative and qualitative data from students who are enrolled in a culturally relevant leadership development program for Pacific Islanders in Southern California. We examine how students' identity, relationships, and leadership is related to their identity and histories.

**Verdict:** _____

---

##  14. [W2951302004](https://openalex.org/W2951302004) — 2019 — article — `uniform`

**Concepts:** Process (computing) (0.64), Context (archaeology) (0.62), Computer science (0.59), Driving simulator (0.53), Point (geometry) (0.44)

**Title:** A Game-Based Driving Learning System for Sri Lankan Driving Learners to Enrich the Awareness of Road Rules

> Traffic safety is becoming an important problem in most of the countries. Based on investigations it has been identified that the unawareness of road rules, lack of practice of sudden reactions in hazardous situations are the major causes for accidents. Though there are many driving simulators available, most of them have not addressed the road rules and hazardous incidences that a driver must be aware. Also they are lacking of a proper evaluation of the driving skills and awareness of the driver. Primary objective of the system is to provide a driving learning platform for the learners, trainers as well as evaluators to overcome the existing challenges, which has mainly focused on creating a virtual environment to facilitate the training and testing process in the local context and main areas of violating road rules and regulations by drivers are taken into account. In order to provide a realistic road environment, virtual environments are modeled based on different criteria. Artificial Intelligence techniques like non-player characters and objects, are employed. One of the major components of the simulator is the driver evaluation: a point based method defined upon the rules, road conditions and driving ethics established in the country. Further, the virtual environment provides all the road conditions available, countryside as well as the urban traffic conditions with different weather conditions. The effectiveness of the developed simulator is measured by allowing a selected group of learners to use the simulator for a specific period and assess their driving skills. It can be concluded that training the learners in a virtual environment that similar to the real environment with a proper assessment of their driving skills, awareness of the rules and road signs, and the driving ethics will solve most of the problems we face today.

**Verdict:** _____

---

##  15. [W4251091456](https://openalex.org/W4251091456) — 2019 — article — `uniform`

**Concepts:** Computer science (0.40)

**Title:** Contributors

> Voelcker worked at Spectrum in the late 1980s, at Green Car Reports in the 2010s, and at a dozen media and tech companies in between. In his spare time, he tinkers with old British cars, a retro pursuit he balances with a focus on the future of transportation. The latter interest recently took him to Porsche's R&D center in Weissach, Germany, where he witnessed really fast electricvehicle charging [see "Porsche's Fast-Charge Power Play," p. 30].

**Verdict:** _____

---

##  16. [W3096684918](https://openalex.org/W3096684918) — 2020 — article — `uniform`

**Concepts:** Filter (signal processing) (0.60), Computer science (0.60), Algorithm (0.58), Filter design (0.57), Minification (0.54)

**Title:** Low Complexity FIR Filter Design using Biogeography Optimization Algorithm and its Improved Version

> In this paper, sparse FIR filter design using multiobjective bio geography based optimization is considered. The metaheuristic bio geography based optimization algorithm is inspired by geographical science. It is easier in implementation, robust and faster in convergence. The objective function of filter design includes minimization of pass band ripples and stop band ripples. The tradeoff between the pass band ripple and stop band ripple cannot be solved by a single objective function and therefore a multiobjective optimization problem is formulated to solve the filter design problem. The evaluation of the proposed method is divided into two parts. In the first part, sparse FIR filter designed with the desired filter specification. In the second part, designed sparse FIR filter compared with the existing reporting algorithms. The comparison result shows the proposed method performs better than the existing algorithm and can be used in practical application.

**Verdict:** _____

---

##  17. [W7024659885](https://openalex.org/W7024659885) — 2004 — article — `uniform`

**Concepts:** Theology (0.49), Physics (0.37), Philosophy (0.32), Croatian (0.28), Traditional medicine (0.25)

**Title:** Stoljeće rearanžiranja: nanoznanost i globalno društvo

> Esej "Stoljeće rearanžiranja: nanoznanost i globalno društvo", dovodi u vezu modernu znanost (nanoznanost) i moderno društvo (globalno društvo) kroz odnos nanotehnologizacije i globalizacije kao najvažnijih procesa jedne mreže fenomena koji se dotiču na području tehničkih i društvenih znanosti. Autor karakterizira 21. stoljeće kao stoljeće rearanžiranja u kojem znanost i filozofija funkcioniraju sa zajedničke osnove koja je holistička i pragmatička. Komparacijom novih tehničkih metoda u znanostima o materijalima i novih procesa u društvenoj ontologiji autor stavlja u odnos dva pristupa i dvije skale identifikacije i reprezentacije: nanoskalu na području zananosti ο materijalima i globalnu skalu na području znanosti ο društvenim odnosima. Tehničke znanosti u formi nanoznanosti orijentirane su na stvaranje nove infrastrukturne paradigme: "ambijenta inteligentnog prostora" vođenog idejom "svi-u-digitalnom-svijetu". Društvene znanosti, koje sudjeluju na planu integracije i globalizacije, orijentirane su na stvaranje nove transnacionalne i spekulativne paradigme: "mobilnog hiper-prostora za internacionalno poslovanje" vođene idejom "svi-u-demokratskom-svijetu". Obje vrste znanosti proizvode istu vrstu nevidljive ontologije koja je dostupna samo virtualnoj identifikaciji i reprezentaciji zasnovanoj na osmišljavanju, stvaranju i proizvodnji programibilne supstancije i programibilnog identiteta. One produciraju identičnost / uniformnost u funkcionalnom operiranju tehničkim sredstvima i političkim principima. U sintagmi "društvo zasnovano na znanju" termin "znanje" ima značenje "znanje proizvodnje, znanje upotrebe i znanje operiranja pametnim (programibilnim) materijalima i pametnim (programibilnim) identitetom". U "D&D svijetu" (digitalnom & demokratskom svijetu) svi ljudi moraju znati upotrebljavati tehnološki mikro-svijet i politički makro-svijet kako bi postigli isti cilj: kontrolu nad prirodom i društvom. Nevidljivost ili iščezavanje realnih stvari, realnih sredstava komunikacije i realnih društvenih odnosa, jeste novo tehničko i ideološko sredstvo stvaranja "novog čarobnog svijeta".

**Verdict:** _____

---

##  18. [W7141945970](https://openalex.org/W7141945970) — 2026 — preprint — `uniform`

**Concepts:** Physics (0.61), Electromagnetic shielding (0.46), Multiplet (0.45), Nonlinear system (0.41), Dark energy (0.38)

**Title:** Chronowaves as a New Communication Channel

> Abstract This paper provides a theoretical and engineering framework for a novel communication channel based on the temporal multiplet (field φ) within the Temporal Theory of the Universe (TTU). Addressing the fundamental limits of the electromagnetic paradigm — spectral congestion and EMI shielding — we propose a transition to Layer 0: the spacetime substrate. The information carrier is defined as a scalar chronowave, a longitudinal perturbation of time density. We analyze the pre-cursor effect, where substrate phase-state shifts precede the inertial response of matter, creating an informational lead time. The proposed architecture utilizes geometric signal amplification (Kozyrev focus) and a multi-tier detection stack (quantum, mechanical, and resonant). We formalize the "Dark Channel" protocol (CW-PSK, Kiev Correlation Protocol), ensuring signal permeability through plasma and metallic barriers. Historical anomalies (EM Drive, superconductivity) are unified under a predicted 0.45 MHz universal resonance, transitioning astronomical observation from passive retrospection to an operational present. Keywords: Chronowave, Layer 0, TTU/TTG, pre-cursor effect, 0.45 MHz resonance, scalar perturbation, disformal coupling, "Dark Channel", operational present. TABLE OF CONTENTS 1. Introduction: Crisis of the Energy Paradigm 1.1. Maxwell's Limits: "Spectral Hunger" and the Energy Dead End 1.2. The Shielding Problem: Where Light is Powerless 1.3. Paradigm Shift: From Photons to Substrate Structure 2. Physics of the Carrier: The Temporal Multiplet and the φ Field 2.1. The φᵃ Substrate: The Fundamental "Data Bus" of the Universe 2.2. Disformal Coupling: Logarithmic Potential and Nonlinearity 2.3. Chronowave as a Scalar: Longitudinal Perturbations vs. EM Waves 3. The Precursor Effect: Informational Lead Time (v ≈ c) 3.1. Event Separation: Phase vs. Inertia 3.2. Lead Time Calculation (Δt): The Accumulated Lag Formula 3.3. Causality Compliance: Why This Is Not FTL 4. Geometric Amplification: The Kozyrev Focus 4.1. The Mirror as a Lens for Time: Compressing the Structure 4.2. The Local Differential Principle: The "Knife" Cutting Through Time 4.3. Gain Coefficient (G_geo): Paraboloid Geometry 5. The Tiered Hardware Stack: Detection Methods 5.1. Quantum Detector (Casimir Effect): Vacuum Pressure 5.2. Macro-Mechanical Sensor (Torsion Balance): Temporal Wind 5.3. Resonant Transducer: Tungsten and Quartz 5.4. Differential Bridge (Wheatstone–Kozyrev) 6. Layer 0 Protocol: Encoding and Super-Permeability 6.1. Phase Modulation (CW-PSK): Digital Signal in Temporal Potential 6.2. Kiev Correlation Protocol: Clarity from Noise 6.3. Engineering the "Dark Channel": Through Plasma and Steel 7. Conclusion: A New Era of Temporal Monitoring 7.1. Summary: The Superiority of the "Dark Channel" 7.2. Falsifiability of the Theory: Experimental Trigger 7.3. Operational Present: From Observer to Actor Appendix A. Historical Context and Unification of Anomalous Phenomena Within the Temporal Theory of the Universe (TTU)

**Verdict:** _____

---

##  19. [W6967989941](https://openalex.org/W6967989941) — 2024 — article — `uniform`

**Concepts:** Knowledge management (0.46), Data management (0.45), Process management (0.41), Computer science (0.39), Work (physics) (0.34)

**Title:** Annex 3 Communication and Data Management Guidelines for CoARA Working Groups

> Communication and Data Management Guidelines for CoARA WGs. The current version is under community review by CoARA WG Co-chairs.

**Verdict:** _____

---

##  20. [W4382462104](https://openalex.org/W4382462104) — 2023 — article — `uniform`

**Concepts:** Smoothing (0.88), Computer science (0.65), Algorithm (0.64), Global Positioning System (0.59), Noise (video) (0.58)

**Title:** An Optimal Carrier-Phase Smoothing Code Algorithm for Low-Cost Single-Frequency Receivers

> Carrier-phase smoothing code (CPSC) is a code-smoothing technology that uses carrier-phase changes to reduce code noise in Global Navigation Satellite System (GNSS) appliances. Although CPSC performs well in reducing noise and is easy to implement, it is a trade-off between the reduction of noise and the increase of the variation of ionospheric errors. The width of the smoothing window needs to be large to reduce noise. However, a wider smoothing window increases the variation of ionospheric errors. To circumvent this dilemma, the grid ionospheric model (GIM) was used to estimate the variation of ionospheric errors between consecutive epochs, and a noise estimation method is proposed for low-cost single-frequency receivers. Furthermore, an optimal carrier phase smoothing code (OCPSC) algorithm with an adaptive width smoothing window is proposed to reduce the noise of Global Positioning System (GPS) data. We found that the OCPSC is more robust and its positioning performance is better overall for low-cost single-frequency receivers than is the traditional CPSC. In a static mode, when applying the OCPSC algorithm, the positioning accuracy can be improved by 0.15 m (6%) and 0.06 m (6%) in the horizontal and vertical directions, respectively. These improvements are 0.08 (3%) m and 0.06 m (1%) when a kinematic mode is applied.

**Verdict:** _____

---

##  21. [W2800261196](https://openalex.org/W2800261196) — 2018 — article — `uniform`

**Concepts:** Humanities (0.54), Psychology (0.38), Physics (0.35), Medicine (0.34), Art (0.24)

**Title:** RITMO SAMBA COMO ESTIMULAÇÃO AUDITIVA RÍTMICA E DESEMPENHO DA MARCHA NA DOENÇA DE PARKINSON

> A estimulação auditiva rítmica tem sido utilizada para amenizar as disfunções motoras na doença de Parkinson, no entanto não são evidentes as alterações que a música popular brasileira causa nos parâmetros espaço-temporais e desempenho funcional da marcha. O objetivo do estudo foi analisar o gênero musical samba durante a marcha de pacientes com doença de Parkinson em situações de dupla tarefa. Estudo de caráter transversal, descritivo e exploratório; cinco indivíduos atenderam aos critérios propostos e realizaram o Timed Up and Go Test nas situações sem música e música popular brasileira (samba) sensibilizadas com tarefas cognitivas e motoras para análise da marcha. Análise estatística descritiva e inferencial com teste de Fridman e post-hoc de Wilcoxon pareado (nível de significância de 5%). Evidenciou-se que o samba associado a uma tarefa motora reduziu a velocidade (p=0,01) e o comprimento de passos (p=0,04) quando comparados à condição de teste sem música. Ouvir música proporcionou maiores demandas atencionais, resultando na adoção de estratégias para diminuir as exigências de equilíbrio postural como a redução do comprimento do passo e velocidade e desta forma diminuir o risco de quedas em situações de duplas tarefas enquanto escuta música.

**Verdict:** _____

---

##  22. [W2588880359](https://openalex.org/W2588880359) — 2018 — article — `uniform`

**Concepts:** Theology (0.84), Physics (0.41), Philosophy (0.33)

**Title:** Analiza uwarunkowań społeczno-kulturowych wpływających na sytuację romskiego ucznia w polskim systemie edukacji

> W systemie wartości Romow wymiar edukacji zajmuje podrzedne miejsce. Dlatego Romowie pośrod innych grup etnicznych zamieszkujących Polske stanowią spolecznośc o najnizszym poziomie wyksztalcenia. Wśrod czlonkow tej grupy nadal klasyfikuje sie bardzo duzo analfabetow i osob z podstawowymi umiejetnościami pisania i czytania. Pomimo iz świadomośc edukacyjna, zwlaszcza mlodych pokolen, wzrasta, starsi Romowie do spraw nauki podchodzą  z dystansem i pewną dozą niecheci. Fakt niskiej frekwencji uczestnictwa Romow w edukacji czesto utozsamiany jest przez osoby nieznające specyfiki kultury romskiej, ich wrodzonym lenistwem i niską inteligencją. Argumenty te, w duzej mierze stereotypowe, w wielu przypadkach nie znajdują potwierdzenia w rzeczywistości. Istotne jest jednak to, iz pomimo tych krzywdzących i wielokrotnie nieprawdziwych ocen Romowie na ogol pozostają bierni i nie probują ich zmienic. Podobnie jest w kwestii inicjatywy tworzenia wlasnych instytucji edukacyjnych i kulturowych, do zakladania ktorych spolecznośc romska ma pelnie praw, jednocześnie ich nie wykorzystując. Romowie, bedąc obywatelami Polski, zobligowani są do przestrzegania obowiązującego w niej prawa, w tym czynnego uczestnictwa w procesie edukacyjnym. Jednak wielu Romow nie wypelnia obowiązku szkolnego, co ukazują chocby statystyki dotyczące liczby romskich absolwentow. Co jest wiec przyczyną niecheci Romow do nauki oraz jakie trudności napotyka romski uczen  w polskiej szkole? Na te i inne pytania odpowiadam w niniejszym artykule, ktorego celem jest ukazanie „barier” wynikających ze specyficznej kultury Romow, stojących na drodze do sukcesow edukacyjnych romskich uczniow.

**Verdict:** _____

---

##  23. [W2054013488](https://openalex.org/W2054013488) — 1997 — article — `uniform`

**Concepts:** Optics (0.78), Laser (0.70), Laser linewidth (0.68), Physics (0.67), Compton scattering (0.45)

**Title:** Compton backscattering focused x-ray source for advanced biomedical applications

> At ultrahigh intensities, where the normalized vector potential of the laser wave exceeds unity, the electron axial velocity modulation due to radiation pressure yields nonlinear Compton backscattered spectra. For applications requiring a narrow Doppler upshifted linewidth, such as the gamma-gamma collider or focused x-ray generation, this can pose a serious problem. It is shown that temporal laser pulse shaping using spectral filtering at the Fourier plane of a chirped pulse laser amplifier can alleviate this problem, and that this technique can be scaled to the required multi-TW range. Compton backscattered spectra are derived in three cases: hyperbolic secant, hybrid pulses (hyperbolic secant trnasient and flat-top), and square optical pulses similar to those experimentally obtained by Weiner et al. It is found that the optimum laser pulse shapes correspond to square pulses, yielding a high contrast ratio between the main spectral line and the transient lines. The corresponding spectral filter function is also determined, and its practical implementation in a chirped pulse laser amplifier is addressed.

**Verdict:** _____

---

##  24. [W4387113806](https://openalex.org/W4387113806) — 2023 — preprint — `uniform`

**Concepts:** Supply chain (0.81), Autoencoder (0.74), Computer science (0.65), Artificial intelligence (0.56), Deep learning (0.47)

**Title:** Disruption Detection for a Cognitive Digital Supply Chain Twin Using Hybrid Deep Learning

> Purpose: Recent disruptive events, such as COVID-19 and Russia-Ukraine conflict, had a significant impact of global supply chains. Digital supply chain twins have been proposed in order to provide decision makers with an effective and efficient tool to mitigate disruption impact. Methods: This paper introduces a hybrid deep learning approach for disruption detection within a cognitive digital supply chain twin framework to enhance supply chain resilience. The proposed disruption detection module utilises a deep autoencoder neural network combined with a one-class support vector machine algorithm. In addition, long-short term memory neural network models are developed to identify the disrupted echelon and predict time-to-recovery from the disruption effect. Results: The obtained information from the proposed approach will help decision-makers and supply chain practitioners make appropriate decisions aiming at minimizing negative impact of disruptive events based on real-time disruption detection data. The results demonstrate the trade-off between disruption detection model sensitivity, encountered delay in disruption detection, and false alarms. This approach has seldom been used in recent literature addressing this issue.

**Verdict:** _____

---

##  25. [W2039744893](https://openalex.org/W2039744893) — 2010 — article — `uniform`

**Concepts:** Jamming (0.85), Frequency-shift keying (0.81), Additive white Gaussian noise (0.80), Fading (0.66), Nakagami distribution (0.55)

**Title:** Performance analysis of FFH/MFSK receivers with noise‐normalisation combining over Nakagami‐<i>m</i>fading channels with partial‐band jamming

> Abstract The performance of a fast frequency‐hopped M ‐ary orthogonal frequency‐shift‐keying (FFH/MFSK) receiver with noise‐normalisation combining over Nakagami‐ m fading channels with partial‐band noise jamming and additive white Gaussian noise (AWGN) is analysed. Instead of numerical integration, a closed‐form error probability expression is obtained. The analytical results validate the simulation results. It is shown that there is an optimum diversity order and the corresponding best‐case performance is investigated. Copyright © 2010 John Wiley &amp; Sons, Ltd.

**Verdict:** _____

---

##  26. [W4414345173](https://openalex.org/W4414345173) — 2025 — article — `uniform`

**Concepts:** Quantum entanglement (0.85), Physics (0.72), Quantum mechanics (0.57), Statistical physics (0.54), Quantum (0.54)

**Title:** Quantum Information Perspective on Many-Body Dispersive Forces

> Despite its ubiquity, the quantum many-body properties of dispersion remain poorly understood. Here, we investigate the entanglement distribution in assemblies of quantum Drude oscillators, minimal models for dispersion-bound systems. We establish an analytic relationship between entanglement and correlation energy and show how entanglement monogamy determines whether many-body corrections to the pair potential are attractive, repulsive, or zero. These findings, demonstrated in trimers and extended lattices, apply in more general chemical environments where dispersion coexists with other cohesive forces.

**Verdict:** _____

---

##  27. [W7099199220](https://openalex.org/W7099199220) — 2009 — article — `uniform`

**Concepts:** Clutter (0.77), Point target (0.67), Algorithm (0.63), Track-before-detect (0.60), Robustness (evolution) (0.59)

**Title:** Particle Filter Based Algorithm for StateEstimation of Dim Moving Point Targets in

> Abstract—Under the condition of the targets ’ initial information is already estimated successfully, This paper presents a real-time target tracking method based on particle filter (PF) update algorithm. According to the particles &amp;apos; transmission characteristics and the measurements from a single frame detection, the algorithm estimate a target’s following moving state. In this way, the dim moving point target could be tracked successfully under the low signal-noise-ratio (SNR) in IR image sequence. But it comes to the multiple targets ’ tracking; we should take the data integration into account. In order to reduce the amount of calculation, we use the data fusion method to divide the measurements in the overlapped parts of windows, appoints the measurements for the corresponding target. That is the Nearest Neighbor Standard Filter (NNSF) theory is used to choose the target for a measurement. The paper introduced the related theory and the concrete steps for accomplish the algorithm and also simulated the proposed tracking algorithm on the MATLAB platform. Experimental analysis and results showed that the algorithm achieved real-time, dynamic stability and robustness while track the random moving targets in high clutter environment. Index Terms—particle filter, single frame detection, measurement division, state estimation, image sequence I.

**Verdict:** _____

---

##  28. [W2603876198](https://openalex.org/W2603876198) — 2016 — article — `uniform`

**Concepts:** Task (project management) (0.69), Object (grammar) (0.57), Physical medicine and rehabilitation (0.54), Computer science (0.47), Artificial intelligence (0.33)

**Title:** Credit Assignment across Limbs in a Bimanual Object Lifting Task (P4.063)

> Objective: To examine credit assignment during a natural object lifting task. Background: Despite our generally skilled interactions with the environment, the motor system invariably makes mistakes. For example, we may lift an object only to find that it is heavier than predicted. To learn from our mistakes, the cause of the error has to be identified by the motor system, a process termed credit assignment. The present study examined whether small errors in lifting forces generalized across limbs as a test of whether they are attributed to the self as opposed to the external environment. If the errors in lifting are attributed to the self, the accumulation of error should remain with the hand performing the lift. Methods: Twenty-nine students completed a bimanual object lifting task. The participant’s left hand always lifted the same block, whereas the right hand lifted a block that gradually increased in weight every ten trials. Following eighty lifts in which the weight in one hand gradually increased, the participant lifted a set of new blocks using a crossed-arm lifting style (lifting the block on the left with the right hand). The initial peak in load force rate (PkLFR) and the load force at the peak load force rate (LF@PkLFR), measures known to be sensitive to a participant’s weight prediction, were examined. Results: PkLFR and LF@PkLFR increased in the right hand between the first and last trial, indicating participants accommodated the change in object weight. However, during the crossed-arm object lifting trials, no differences between the hands were observed. Conclusions: This research suggests small errors in motor control are not always attributed to the self, and may at times be attributed to the external environment. By learning how error-based learning is accomplished, we can create better artificial limbs and more thoroughly assess motor impairments.

**Verdict:** _____

---

##  29. [W2035540682](https://openalex.org/W2035540682) — 1995 — article — `uniform`

**Concepts:** Citation (0.72), Altmetrics (0.67), Icon (0.63), Computer science (0.45), World Wide Web (0.28)

**Title:** Bond Strength Trends in Halogenated Methanols: Evidence for Negative Hyperconjugation?

> ADVERTISEMENT RETURN TO ISSUEPREVArticleNEXTBond Strength Trends in Halogenated Methanols: Evidence for Negative Hyperconjugation?William F. Schneider, Barbara I. Nance, and Timothy J. WallingtonCite this: J. Am. Chem. Soc. 1995, 117, 1, 478–485Publication Date (Print):January 1, 1995Publication History Published online1 May 2002Published inissue 1 January 1995https://pubs.acs.org/doi/10.1021/ja00106a055https://doi.org/10.1021/ja00106a055research-articleACS PublicationsRequest reuse permissionsArticle Views286Altmetric-Citations53LEARN ABOUT THESE METRICSArticle Views are the COUNTER-compliant sum of full text article downloads since November 2008 (both PDF and HTML) across all institutions and individuals. These metrics are regularly updated to reflect usage leading up to the last few days.Citations are the number of other articles citing this article, calculated by Crossref and updated daily. Find more information about Crossref citation counts.The Altmetric Attention Score is a quantitative measure of the attention that a research article has received online. Clicking on the donut icon will load a page at altmetric.com with additional details about the score and the social media presence for the given article. Find more information on the Altmetric Attention Score and how the score is calculated. Share Add toView InAdd Full Text with ReferenceAdd Description ExportRISCitationCitation and abstractCitation and referencesMore Options Share onFacebookTwitterWechatLinked InRedditEmail Other access optionsGet e-Alertsclose Get e-Alerts

**Verdict:** _____

---

##  30. [W2804252553](https://openalex.org/W2804252553) — 2018 — article — `uniform`

**Concepts:** Computer science (0.68), Reliability (semiconductor) (0.67), Demand response (0.61), Reliability engineering (0.55), Renewable energy (0.53)

**Title:** i13DR

> With the ongoing integration of Renewable Energy Sources (RES), the complexity of power grids is increasing. Due to the fluctuating nature of RES, ensuring the reliability of power grids can be challenging. One possible approach for addressing these challenges is Demand Response (DR) which is described as matching the demand for electrical energy according to the changes and the availability of supply. However, implementing a DR system to monitor and control a broad set of electrical appliances in real-time introduces several new complications including ensuring reliability and financial feasibility of the system. In this work, we address these issues by designing and implementing a distributed real-time DR infrastructure for laptops, which estimates and controls the power consumption of a network of connected laptops in response to the fast irregular changes of RES. The result of our field experiments confirms that our system successfully schedules and executes rapid and effective DR events. However, the accuracy of estimated power consumption of all participating laptops is relatively low, directly caused by our software-based approach.

**Verdict:** _____

---

##  31. [W7111010977](https://openalex.org/W7111010977) — 2025 — article — `uniform`

**Concepts:** Materials science (0.65), Photonics (0.60), Transistor (0.52), Optoelectronics (0.50), Broadband (0.49)

**Title:** Organic PhotonicSynapses with UV–Vis–NIRBroadband Perception Based on Organic Electrochemical Transistors

> Organic photonic synaptic devices have shown immense potential for emulating the visual perception function of the human retina. In particular, organic electrochemical transistors (OECTs) with photoresponse ability are considered promising choices because of their advantages in low-voltage operation, mechanical flexibility, and biocompatibility. However, current research is limited, and deeper investigations into the materials, devices, and their perception capability are needed. Herein, we introduce a solid-state organic electrochemical transistor based on an organic bulk heterojunction film, which exhibits a broadband response from ultraviolet to near-infrared (365–850 nm) and can simulate fundamental biological synaptic behaviors across multiple wavelengths. Moreover, the device can emulate the learning, forgetting, and relearning processes, as well as the image recognition and memory functions. By employing a trichromatic perception simulation based on convolutional operations, the device successfully achieves image preprocessing capabilities, demonstrating the promising potential of our OECT-based photonic synapses in artificial visual perception systems.

**Verdict:** _____

---

##  32. [W4242183320](https://openalex.org/W4242183320) — 1988 — article — `uniform`

**Concepts:** Computer science (0.31)

**Title:** AAAS-African Programs Under Way

> Article MetricsDownloadsCitationsNo data available.012AugSepOctNovDecJan810Total6 Months12 MonthsTotal number of downloads for the most recent 6 whole calendar months.

**Verdict:** _____

---

##  33. [W4322731357](https://openalex.org/W4322731357) — 2020 — book-chapter — `uniform`

**Concepts:** Surprise (0.87), Backcasting (0.69), Futures contract (0.68), Curriculum (0.61), Key (lock) (0.60)

**Title:** Key Messages

> We are facing unprecedented challenges – social, economic and environmental – driven by accelerating globalisation and a faster rate of technological developments. At the same time, those forces are providing us with myriad new opportunities for human advancement. The future is uncertain and futures often surprise us; but we need to be open and ready for it and we can also surprise our future. Some strategies include: 1) forecasting future needs of society and actively taking into account the students' needs, interests and voices when designing curriculum, and 2) backcasting, i.e. articulating a shared vision for student profiles as desired student outcomes, then looking back to today to identify curriculum changes necessary to achieve the shared vision.

**Verdict:** _____

---

##  34. [W2378887358](https://openalex.org/W2378887358) — 2013 — article — `uniform`

**Concepts:** Generality (0.75), Test (biology) (0.65), Computer science (0.54), Process (computing) (0.50), Test data (0.45)

**Title:** The Generality and Analysis of Engine Performance Test

> This paper has generally discussed some problems during engine performance test and makes some summarizations about data analysis and equipment of engine performance test combined with actual situations.Summarized in this paper about how to complete the engine performance experiment effectively,and induced how to solve the test problems that you may encounter in the process of experiment.

**Verdict:** _____

---

##  35. [W7014994288](https://openalex.org/W7014994288) — 2000 — article — `uniform`

**Concepts:** Underwater acoustic communication (0.73), Underwater (0.70), Acoustics (0.58), Underwater acoustics (0.52), Computer science (0.51)

**Title:** The ROBLINKS underwater acoustic communication experiments:

> Within the EU-MAST III project ROBLINKS waveforms and algorithms have been developed to establish robust underwater acoustic communication links with high data rates Ã­n shallow water. To evaluate the signalling schemes a wide range of experiments has been performed during a sea trial that has been held in May 1999 in the North Sea, off rhe Dutch coast. The resulting data set consists of recordings of the newly developed waveforms, of more conventional communication signals for comparison, and of signals to probe the acoustic channel. Environmental data have also been collected to analyze and understand the propagation conditions during the transmissions. The most interesting and illustrative part of the data set will be made available for further analysis after the end of the ROBLINKS project

**Verdict:** _____

---

##  36. [W2077685954](https://openalex.org/W2077685954) — 1966 — article — `uniform`

**Concepts:** Bibliography (0.91), Computer science (0.55), Library science (0.37), Information retrieval (0.36), Political science (0.35)

**Title:** Soviet Centralized Bibliography

> After pointing to the critical need for comprehensive world bibliography both current and retrospective, the author describes the structure of Soviet bibliographic coverage. He gives reasons for certain aspects of Soviet bibliography which have on occasion in the past been criticized and describes some of the particular problems encountered in enumerating the productions of the Soviet press. He concludes with a statement concerning some of the weaknesses remaining in the Soviet system and describes prospects for their elimination.

**Verdict:** _____

---

##  37. [W2754810232](https://openalex.org/W2754810232) — 2017 — article — `uniform`

**Concepts:** Exponential stability (0.82), Artificial neural network (0.60), Exponential function (0.55), Control theory (sociology) (0.54), Mathematics (0.54)

**Title:** Almost sure exponential stability of stochastic Cohen-Grossberg neural networks with Markovian jumping and impulses

> By employing the Lyapunov function method and average impulsive interval approach, the almost sure exponential stability for stochastic Cohen-Grossberg neural networks with Markovian jumping and impulses are considered. A set of sufficient conditions of almost sure exponential stability are derived. An example is given to illustrate the effectiveness of the results obtained.

**Verdict:** _____

---

##  38. [W2147043418](https://openalex.org/W2147043418) — 2014 — article — `uniform`

**Concepts:** Mach number (0.82), Aerodynamics (0.62), Cylinder (0.61), Reynolds number (0.61), Physics (0.59)

**Title:** Towards Simulation of Far-Field Aerodynamic Sound from a Circular Cylinder Using OpenFoam

> The low-Mach number flow-induced noise by the flow past a circular cylinder at sub-critical regime was predicted. First, to assess the accuracy of the numerical methodology, the laminar flow over a circular cylinder at the Reynolds number Re = 140 and Mach number M = 0.2 was calculated by direct solution of the unsteady compressible Navier-Stokes equations. Second, the sound generated by a circular cylinder at the Reynolds number Re = 2.2 × 10 4 and Mach number M = 0.06 was simulated using a technique of large-eddy simulation. For both cases, the calculated acoustic fields showed a dipole directivity, similar to a natural vortex shedding. The impact of the Doppler effect was investigated and discussed as well. In general, the computed aerodynamic and far-field acoustic results were found to be in good agreement with available experimental measurements and analytical relationships.

**Verdict:** _____

---

##  39. [W2365176882](https://openalex.org/W2365176882) — 2012 — article — `uniform`

**Concepts:** Bridge (graph theory) (0.84), Wireless (0.59), Wireless network (0.56), Field (mathematics) (0.55), Wireless transmission (0.54)

**Title:** Application of wireless bridge to field water system

> It's important that real-time monitoring and the unified production management in the field scattered deep well pump house.Application of wireless bridge will realize systematic data live transmission,we can monitor the parameters'change which in the CCR may be clear at a glance,simultaneously we can check all pump house through the real-time video,the entire pump house realizes 24 hours unattended running;Application of wireless bridge in system is more easier to build and more cheaper then the traditional wired network,the network run cost approaches in zero,manpower and material resources can be reduced greatly.

**Verdict:** _____

---

##  40. [W2007040212](https://openalex.org/W2007040212) — 2010 — article — `uniform`

**Concepts:** Physics (0.58), Molecular biology (0.35), Biology (0.16)

**Title:** CITOLOGIA DE LAVADO BRONCOALVEOLAR DE CÃES: COMPARAÇÃO ENTRE LÂMINAS A FRESCO E CONSERVADAS EM FORMOL

> O lavado broncoalveolar em cães é um método diagnóstico recomendado em casos de enfermidades do trato respiratório inferior, quando exames de rotina não permitem um diagnóstico conclusivo. O exame baseia-se na análise citológica e confecção de lâminas com o material a fresco, ou seja, logo após a coleta, o que pode inviabilizar a técnica em casos de difícil acesso aos laboratórios especializados. Para isso, faz-se necessário um meio de conservação das amostras, aumentando o tempo de vida útil do material a ser analisado. Assim, realizou-se o lavado broncoalveolar em quatorze cães adultos saudáveis. As amostras foram separadas em duas alíquotas: a primeira confeccionada a fresco por sedimentação em câmara de Suta, e a segunda processada uma semana depois, com a amostra conservada em formol. As lâminas foram coradas pelo corante rápido Panótico. Avaliou-se o volume infundido e o volume recuperado, o aspecto macroscópico, a contagem de células nucleadas, a análise diferencial de células e a análise descritiva das lâminas quanto à celularidade, presença de muco, hemácias, leucócitos e células, íntegras ou degeneradas. A análise estatística foi realizada com teste t, para amostras pareadas com p&lt;0,05. Foram encontrados aumento significativo na quantidade de linfócitos e diminuição do número de macrófagos nas amostras conservadas em formol. As demais observações foram similares em ambos os grupos. Portanto, a conservação do material do lavado broncoalveolar de cão em formol, durante uma semana, preservou as células, tornando viável a técnica do lavado broncoalveolar.

**Verdict:** _____

---

##  41. [W3044815875](https://openalex.org/W3044815875) — 2020 — review — `uniform`

**Concepts:** Facial recognition system (0.75), Computer science (0.72), Three-dimensional face recognition (0.67), Identification (biology) (0.59), Artificial intelligence (0.59)

**Title:** Past, Present, and Future of Face Recognition: A Review

> Face recognition is one of the most active research fields of computer vision and pattern recognition, with many practical and commercial applications including identification, access control, forensics, and human-computer interactions. However, identifying a face in a crowd raises serious questions about individual freedoms and poses ethical issues. Significant methods, algorithms, approaches, and databases have been proposed over recent years to study constrained and unconstrained face recognition. 2D approaches reached some degree of maturity and reported very high rates of recognition. This performance is achieved in controlled environments where the acquisition parameters are controlled, such as lighting, angle of view, and distance between the camera–subject. However, if the ambient conditions (e.g., lighting) or the facial appearance (e.g., pose or facial expression) change, this performance will degrade dramatically. 3D approaches were proposed as an alternative solution to the problems mentioned above. The advantage of 3D data lies in its invariance to pose and lighting conditions, which has enhanced recognition systems efficiency. 3D data, however, is somewhat sensitive to changes in facial expressions. This review presents the history of face recognition technology, the current state-of-the-art methodologies, and future directions. We specifically concentrate on the most recent databases, 2D and 3D face recognition methods. Besides, we pay particular attention to deep learning approach as it presents the actuality in this field. Open issues are examined and potential directions for research in facial recognition are proposed in order to provide the reader with a point of reference for topics that deserve consideration.

**Verdict:** _____

---

##  42. [W4230054203](https://openalex.org/W4230054203) — 2000 — article — `uniform`

**Concepts:** Intrinsics (0.98), Stage (stratigraphy) (0.50), Computer science (0.34), Artificial intelligence (0.06), Paleontology (0.00)

**Title:** The Stage View and Temporary Intrinsics

> Four-dimensionalism, as I’ll use the term, is the doctrine that reality is spread out in time as well as space.1 Just as objects that are located at multiple regions of space contain parts conned to those regions of space, so objects that are located at multiple regions of time contain parts — temporal parts — that are conned to those regions of time. (Or better: an object that occupies an extended spatiotemporal region R has parts conned to the various subregions of R; but I’ll ignore this complication henceforth.) Most who accept this ontology of perduring objects, as they are often called, identify the continuants of our everyday ontology with “space-time worms” — mereological sums of stages from different times. Elsewhere (1996) I have proposed a different version of four-dimensionalism, which identies continu-ants with the stages themselves, and which analyses de re temporal predication with a temporal version of modal counterpart theory (Lewis, 1968, 1971). On this view, a current assertion of ‘Clinton was indiscreet ’ is true iff the (current) referent of ‘Clinton ’ — a stage — has an indiscreet temporal counterpart in the

**Verdict:** _____

---

##  43. [W2963807684](https://openalex.org/W2963807684) — 2019 — article — `uniform`

**Concepts:** Cosmic ray (0.89), Physics (0.84), Neutrino (0.80), Observatory (0.76), Neutrino detector (0.62)

**Title:** Cosmic ray composition study using machine learning at the IceCube Neutrino Observatory

> The evaluation of mass composition of cosmic rays in the knee region (~3 PeV) is critical to understanding the transition in the origin of cosmic rays from galactic to extragalactic sources. The IceCube Neutrino Observatory at the South Pole is a multi-component detector consisting of the surface IceTop array and the deep in-ice IceCube detector. By applying modern machine-learning techniques to cosmic-ray air showers reconstructed coincidentally in both detector components of IceCube observatory, the energy and the mass of primary cosmic rays in this transition region can be measured. In this contribution, we will discuss the reconstruction performance and composition sensitivity of IceCube observables presently under development.

**Verdict:** _____

---

##  44. [W1496376740](https://openalex.org/W1496376740) — 2012 — article — `uniform`

**Concepts:** Interfacing (0.90), Electromyography (0.71), Interface (matter) (0.71), Physical medicine and rehabilitation (0.60), Exoskeleton (0.56)

**Title:** Review of EMG-based neuromuscular modeling for the use of upper limb control

> Assistive robots have made great contributions to disabled people in physiotherapy and rehabilitation areas. The interface between patients and medical devices plays a significant role for patients to operate these kinds of robots. This review introduces the current research and development of neuromuscular interfaces, especially the new research directions with special focus on modeling of musculoskeletal systems for interfacing purposes. The paper also summarises the function and prominent advantage of using surface Electromyography (sEMG) signals for the interface. The elbow joint was used as an example to go through the working steps of both human biological systems and neuromuscular interfaces. Further developments were also discussed to improve the interface to meet medical demands.

**Verdict:** _____

---

##  45. [W7037981199](https://openalex.org/W7037981199) — 2000 — article — `uniform`

**Concepts:** Computer science (0.48), Quality (philosophy) (0.47), Artificial intelligence (0.46), Work (physics) (0.44), Odor (0.41)

**Title:** Fisher Information and Optimal Odor Sensors

> This is the author’s version of a work that was accepted for publication in Neurocomputing. Changes resulting from the publishing process, such as peer review, editing, corrections, structural formatting, and other quality control mechanisms may not be reflected in this document. Changes may have been made to this work since it was submitted for publication. A definitive version was subsequently published in Neurocomputing, vol,38-40 (2001) doi:10.1016/S0925-2312(01)00364-2

**Verdict:** _____

---

##  46. [W3035359449](https://openalex.org/W3035359449) — 2020 — article — `uniform`

**Concepts:** Computer science (0.69), Electroencephalography (0.63), Artificial intelligence (0.54), Dependency (UML) (0.50), Brain activity and meditation (0.49)

**Title:** Complex brain activity analysis and recognition based on multiagent methods

> Summary Brain activity recognition research has been a challenging area for many decades since Hans Berger described electroencephalogram (EEG) in 1929. Many previous researches cannot successfully identify EEG status due to dynamic brain activities and complicated brain correlation. This article adopts multiagent‐based methods to analyze EEG datasets, which can enhance the analytical efficiency through incorporating autonomous, self‐coordination characteristics of agents. Intelligent agents are autonomous applications that can improve system compatibility. The preliminary results indicate that the combination of time‐dependency correlation method with multiagent method is an efficient solution for brain activity recognition.

**Verdict:** _____

---

##  47. [W6892051625](https://openalex.org/W6892051625) — 2018 — preprint — `uniform`

**Concepts:** Physics (0.88), Cosmic censorship hypothesis (0.86), Black hole (networking) (0.61), Gravitational wave (0.55), Hawking radiation (0.52)

**Title:** Cosmic censorship violation in black hole collisions in higher dimensions

> We argue that cosmic censorship is violated in the collision of two black holes in high spacetime dimension D when the initial total angular momentum is sufficiently large. The two black holes merge and form an unstable bar-like horizon, which grows a neck in its middle that pinches down with diverging curvature. When D is large, the emission of gravitational radiation is strongly suppressed and cannot spin down the system to a stable rotating black hole before the neck grows. The phenomenon is demonstrated using simple numerical simulations of the effective theory in the 1/D expansion. We propose that, even though cosmic censorship is violated, the loss of predictability is small independently of D.

**Verdict:** _____

---

##  48. [W2322843881](https://openalex.org/W2322843881) — 2014 — preprint — `uniform`

**Concepts:** Plage (0.64), Physics (0.60), Humanities (0.50), Art (0.13), Geology (0.09)

**Title:** Trente-huit ans de rechargements sur la plage de Nice, Côte d’Azur : une synthèse statistique

> Le rivage de la ville de Nice, sur la Cte d'Azur en France, est bord par un troit cordon de galets de 4,5 km le long de la clbre Promenade des Anglais. Cette plage volue dans un contexte de basse nergie, mais connait cependant des problmes d'rosion car elle est trs artificialise, est coupe de ses sources naturelles de sdiments et se situe au niveau d'une avant-cte trs pentue. Depuis 1976, les services techniques de la mairie procdent des mesures de la largeur de la plage au niveau de 50 transects. Afin de lutter contre l'rosion et maintenir une largeur de plage suffisante pour les activits balnaires, la mairie a dpos prs de 600000 m 3 de matriaux de rechargement depuis 38 ans. Nous disposons donc d'une base de donnes pour tudier l'volution de cette plage et estimer l'efficacit de la politique de rechargement.

**Verdict:** _____

---

##  49. [W2744161686](https://openalex.org/W2744161686) — 2017 — article — `uniform`

**Concepts:** Humanities (0.64), Physics (0.48), Political science (0.41), Philosophy (0.19)

**Title:** Décret n<sup>o</sup>2016–1074 relatif à la protection des travailleurs contre les risques dus aux champs électromagnétiques

> Sorti le 3 août 2016 et applicable au premier janvier 2017, le décret 2016–1074 établit des règles et recommandations à suivre pour protéger les travailleurs face aux risques dus aux champs électromagnétiques. Transposant la directive européenne 2013/35/UE, il concerne tout employeur et impose au minimum l'établissement d'une évaluation des risques. Les unités, clinique ou de recherche, utilisant des dispositifs d'imagerie par résonance magnétique (IRM) sont particulièrement concernées. En effet, cette modalité d'imagerie émet des champs électromagnétiques susceptibles d'engendrer des niveaux d'exposition des travailleurs dépassant les valeurs déclenchant l'action et les valeurs limites d'exposition définies par la directive et le décret. Une section de ce dernier lui est d'ailleurs entièrement consacrée. Le présent document propose, en premier lieu, une analyse détaillée du décret 2016–1074 et des obligations de l'employeur. Il propose, dans un second temps, une analyse concernant la mise en application de cette directive et du décret associé pour le dispositif particulier qu'est l'IRM.

**Verdict:** _____

---

##  50. [W2124566158](https://openalex.org/W2124566158) — 2015 — article — `uniform`

**Concepts:** Computer science (0.89), Cognitive radio (0.84), Spectrum (functional analysis) (0.54), Computer network (0.52), Vehicular ad hoc network (0.48)

**Title:** History-based spectrum sensing in CR-VANETs

> Cognitive radio spectrum sensing is an important issue in today’s emerging communication techniques. Similarly, vehicular networks are vital considering the increasing traffic on roads and fatal accidents. Efficient networks can reduce the road accidents and enhance the suitability of communication between vehicles and with fixed infrastructure. Different techniques like independent spectrum sensing and various forms of cooperative techniques have been proposed in the near past. We propose a sensing technique which prepares a database for small road segments, time slots for the hours of the day, and different frequencies of the spectrum based on the sensing of vehicles throughout the day. Based on this database, the future utilization of the spectrum is proposed. Simulations and results clearly indicate the success and usefulness of our proposed technique.

**Verdict:** _____

---

##  51. [W2327918537](https://openalex.org/W2327918537) — 1937 — article — `pre1990`

**Concepts:** Content (measure theory) (0.56), Link (geometry) (0.45), Computer science (0.44), Information retrieval (0.36), Mathematics (0.33)

**Title:** S. C. Kleene. λ-definability and recursiveness. Duke mathematical journal, Bd. 2 (1936), S. 340–353.

> An abstract is not available for this content so a preview has been provided. Please use the Get access link above for information on how to access this content.

**Verdict:** _____

---

##  52. [W2331191781](https://openalex.org/W2331191781) — 1989 — article — `pre1990`

**Concepts:** Ion (0.63), Hydrogen (0.63), Molecule (0.59), Hydrogen molecule (0.51), Atomic physics (0.47)

**Title:** Partial Wave Analysis of Hydrogen Molecule Ion

> A nonadiabatic procedure is proposed to obtain the eigensolutions of the hydrogen molecule ion. The partial wave behavior of the electron and the proton pair in the three lowest states is investigated in detail in this paper. The overlap of nodes for different partial waves of the protons is found.

**Verdict:** _____

---

##  53. [W2159221511](https://openalex.org/W2159221511) — 1986 — article — `pre1990`

**Concepts:** Calibration (0.68), Characterization (materials science) (0.67), Dosimetry (0.64), Physics (0.55), Ionization (0.47)

**Title:** Techniques Of Absolute Low Energy X-Ray Calibration

> Recent advances in pulsed plasma research, materials science, and astrophysics have required many new diagnostic instruments for use in the low energy x-ray regime. The characterization of these instruments has provided a challenge to instrument designers and provided the momentum to improve x-ray sources and dosimetry techniques. In this paper, the present state-of-the-art in low energy x-ray characterization techniques is reviewed. A summary is given of low energy x-ray generator technology and dosimetry techniques including a discussion of thin window proportional counters and ionization chambers. A review is included of the widely used x-ray data bases and a sample of ultra-soft x-ray measuring techniques is discussed. These techniques include sub-femtoampere current measuring procedures, chopped x-ray source generators, phase sensitive detection of ultralow currents, and angular divergence measurements.

**Verdict:** _____

---

##  54. [W4234061041](https://openalex.org/W4234061041) — 1938 — article — `pre1990`

**Concepts:** Section (typography) (0.81), Business (0.40), Computer science (0.38), Political science (0.34), Advertising (0.25)

**Title:** ORGANIZATION SECTION

> <h3>AMERICAN MEDICAL ASSOCIATION STUDY OF MEDICALCARE</h3><h3>Walker County, Alabama</h3> Proceeding with the plan to present some of the reports from county medical societies throughout the country, the information on the Summary Sheet and the accompanying comments for Walker County, Ala., are given. Walker County has a population of 65,000, of which a little over 5,000 live in the city of Jasper. Forty-three forms were sent out to physicians and dentists, of which seventeen were returned. In addition to physicians and dentists two hospitals located in the county, the nurses' organization and the health department all contributed information to the Survey, as did one additional organization. There are thirty-five physicians in active practice, and the greatest distance that the nearest physician would have to travel to reach persons in the area was 15 miles. There were four full-time and three parttime nurses, twelve pharmacists and two hospitals, both of which

**Verdict:** _____

---

##  55. [W4299855127](https://openalex.org/W4299855127) — 1941 — article — `pre1990`

**Concepts:** Icon (0.95), Citation (0.65), Download (0.49), Library science (0.43), Computer science (0.40)

**Title:** “Wild Bill” Donovan

> Essay| April 01 1941 “Wild Bill” Donovan: Lawyer, Soldier and Diplomat, He Acts as the President’s Special Envoy to the World at Large John K. Lagemann John K. Lagemann Search for other works by this author on: This Site PubMed Google Scholar Current History (1941) 52 (11): 23–25. https://doi.org/10.1525/curh.1941.52.11.23 Views Icon Views Article contents Figures & tables Video Audio Supplementary Data Peer Review Share Icon Share Twitter LinkedIn Tools Icon Tools Get Permissions Cite Icon Cite Search Site Citation John K. Lagemann; “Wild Bill” Donovan: Lawyer, Soldier and Diplomat, He Acts as the President’s Special Envoy to the World at Large. Current History 1 April 1941; 52 (11): 23–25. doi: https://doi.org/10.1525/curh.1941.52.11.23 Download citation file: Ris (Zotero) Reference Manager EasyBib Bookends Mendeley Papers EndNote RefWorks BibTex toolbar search Search Dropdown Menu toolbar search search input Search input auto suggest filter your search All ContentCurrent History Search This content is only available via PDF. © 1941 by The Regents of the University of California1941 Article PDF first page preview Close Modal You do not currently have access to this content.

**Verdict:** _____

---

##  56. [W4237217367](https://openalex.org/W4237217367) — 1952 — article — `pre1990`

**Concepts:** Citation (0.73), Altmetrics (0.71), Icon (0.70), Social media (0.60), Computer science (0.58)

**Title:** Advertisement/Classifieds

> ADVERTISEMENT RETURN TO ISSUEPREVArticleNEXTAdvertisement/ClassifiedsCite this: Anal. Chem. 1952, 24, 1, 45APublication Date (Print):January 23, 1952Publication History Published online3 May 2012Published inissue 23 January 1952https://doi.org/10.1021/ac60061a747RIGHTS & PERMISSIONSArticle Views5Altmetric-Citations-LEARN ABOUT THESE METRICSArticle Views are the COUNTER-compliant sum of full text article downloads since November 2008 (both PDF and HTML) across all institutions and individuals. These metrics are regularly updated to reflect usage leading up to the last few days.Citations are the number of other articles citing this article, calculated by Crossref and updated daily. Find more information about Crossref citation counts.The Altmetric Attention Score is a quantitative measure of the attention that a research article has received online. Clicking on the donut icon will load a page at altmetric.com with additional details about the score and the social media presence for the given article. Find more information on the Altmetric Attention Score and how the score is calculated. Share Add toView InAdd Full Text with ReferenceAdd Description ExportRISCitationCitation and abstractCitation and referencesMore Options Share onFacebookTwitterWechatLinked InReddit PDF (258 KB) Get e-Alerts Get e-Alerts

**Verdict:** _____

---

##  57. [W2034796854](https://openalex.org/W2034796854) — 1975 — article — `pre1990`

**Concepts:** Citation (0.65), Altmetrics (0.59), Association (psychology) (0.58), Icon (0.53), Computer science (0.44)

**Title:** Dielectric constant of liquid ammonia from -35 to + 50.deg. and its influence on the association between solvated electrons and cation

> ADVERTISEMENT RETURN TO ISSUEPREVArticleNEXTDielectric constant of liquid ammonia from -35 to + 50.deg. and its influence on the association between solvated electrons and cationGerard Billaud and Antoine DemortierCite this: J. Phys. Chem. 1975, 79, 26, 3053–3055Publication Date (Print):December 1, 1975Publication History Published online1 May 2002Published inissue 1 December 1975https://pubs.acs.org/doi/10.1021/j100593a053https://doi.org/10.1021/j100593a053research-articleACS PublicationsRequest reuse permissionsArticle Views700Altmetric-Citations36LEARN ABOUT THESE METRICSArticle Views are the COUNTER-compliant sum of full text article downloads since November 2008 (both PDF and HTML) across all institutions and individuals. These metrics are regularly updated to reflect usage leading up to the last few days.Citations are the number of other articles citing this article, calculated by Crossref and updated daily. Find more information about Crossref citation counts.The Altmetric Attention Score is a quantitative measure of the attention that a research article has received online. Clicking on the donut icon will load a page at altmetric.com with additional details about the score and the social media presence for the given article. Find more information on the Altmetric Attention Score and how the score is calculated. Share Add toView InAdd Full Text with ReferenceAdd Description ExportRISCitationCitation and abstractCitation and referencesMore Options Share onFacebookTwitterWechatLinked InRedditEmail Other access options Get e-Alerts

**Verdict:** _____

---

##  58. [W2028760745](https://openalex.org/W2028760745) — 1981 — article — `pre1990`

**Concepts:** Cyclotron (0.81), Physics (0.69), Atomic physics (0.66), Ion (0.61), Electron (0.51)

**Title:** The relationship of field‐aligned currents to electrostatic ion cyclotron waves

> Two sources of free energy for driving ion cyclotron waves have been observed on the S3‐3 satellite: field‐aligned currents and ion beams. Since the waves are destabilized by the thermal electron drift and not the current, before correlating observations of field‐aligned currents with ion cyclotron waves, it is first necessary to determine that the current is primarily carried by thermal electrons. Comparisons of the current carried by energetic particles with the current measured by the magnetometer during several events shows that this is sometimes the case. Statistical studies indicate that the field‐aligned current density is correlated with the spectral density during ion cyclotron events. The combination of the results of this report and those of Kintner et al. (1979) is consistent with the hypothesis that the observed ion cyclotron waves are driven by a combination of ion beams and electron drift. However, the available data set does not unambiguously identify the free energy source.

**Verdict:** _____

---

##  59. [W3209271085](https://openalex.org/W3209271085) — 1962 — article — `pre1990`

**Concepts:** Ion (0.80), Atomic physics (0.73), Silicon (0.70), Hydrogen (0.66), Proton (0.60)

**Title:** Response of Silicon Surface Barrier Detectors to Hydrogen Ions of Energies 25 to 250 kev

> Commercially produced silicon surface barrier counters have been exposed at room temperature to hydrogen ion beams varying in energy from 18 to 225 kev and the pulse spectra analyzed. The output has been found to be linear with ion energy. A dead layer equivalent to about 4 kev loss by a 100 kev proton is indicated, suggesting that the gold surface layer is the only dead region. The width of the pulse spectrum is found to be about 9 kev for protons independent of ion energy, and limited by system noise. Multi-atomic ions produce an output a few percent below that expected of an equivalent number of protons of the same velocity. The width of the pulse spectrum is also found to be greater for the multi-atomic ions than for protons.

**Verdict:** _____

---

##  60. [W1488779533](https://openalex.org/W1488779533) — 1981 — article — `pre1990`

**Concepts:** Guideline (0.54), Psychology (0.42), Computer science (0.33), Medical education (0.32), Medicine (0.27)

**Title:** A Personal Guideline for the Use of Correction in the Classroom

> Correction is an important aspect of teaching, one that ESL teachers face daily. At issue is the ability to match the teacher's goals or priorities with what is supposed to be taught or learned, and the specific teaching-learning environment. The study presents my original definition of correction, the beginning reference point for this work, which is eventually compared to a new definition of correction. The evolution of the new definition is based upon documentation and analysis of five case studies and the systematic generation and development of a model for correction use. The model is adaptable for use by any teacher, but necessarily different depending upon that teacher's goals and priorities. The model is flexible and therefore able to accommodate individual teaching-learning environments as well as any changes in personal priorities and goals.

**Verdict:** _____

---

##  61. [W2001348321](https://openalex.org/W2001348321) — 1985 — article — `pre1990`

**Concepts:** Physics (0.80), General relativity (0.75), Dirac (video compression format) (0.67), Einstein (0.58), Theory of relativity (0.54)

**Title:** On solutions of the Einstein-Cartan-Dirac theory

> Considers the relation between the general theory of relativity and the Einstein-Cartan theory in the case that matter is described by a Dirac field. Thereby the author finds the condition that an (arbitrary) solution of general relativity with a Dirac field is also a solution of the Einstein-Cartan-Dirac theory and vice versa. Exploiting this result the author generates new non-ghost solutions of the Einstein-Cartan-Dirac theory from ghost solutions of general relativity.

**Verdict:** _____

---

##  62. [W238155183](https://openalex.org/W238155183) — 1981 — article — `pre1990`

**Concepts:** Safety stock (0.82), Inventory investment (0.59), Operations research (0.54), Stock (firearms) (0.53), Economic order quantity (0.51)

**Title:** Relating Expected Inventory Backorders to Safety Stock Investment Levels.

> The objective of this research was to develop a method to define and predict the relationship between inventory performance and safety stock investment for the Defense Electronics Supply Center (DESC) inventory. DESC uses the model prescribed by DoD Instruction 4140.39 to set individual item safety stock levels. This model minimizes the sum of the variable order and holding costs subject to a constraint on the expected inventory perofmrance as measured by the number of time-weighted essentiality-weighted requisitions short (backorders). An important consideration in selecting the constraint for this model is the safety stock investment required for various levels of performance. This thesis uses multi-variate regression analysis and forecasting techniques to predict the relationship between expected performance and required investment. The author concludes that this method produces accurate predictions of the relationship. The recommended model produced average absolute errors of about three percent when tested against historical data from the DESC inventory. (Author)

**Verdict:** _____

---

##  63. [W79240188](https://openalex.org/W79240188) — 1981 — article — `pre1990`

**Concepts:** Noise barrier (0.91), Roadway noise (0.65), Transport engineering (0.61), Noise (video) (0.58), Engineering (0.47)

**Title:** HIGHWAY NOISE BARRIERS

> This summary of progress on highway noise barriers gives quantitative and qualitative perspectives of the design, construction, maintenance, and impacts of the barriers that have been built to mitigate excessive highway noise. The Federal Highway Administration (FHWA) design noise levels are the principal criterion used to determine height and length of a barrier. Most states will not install a barrier unless it will result in a noise reduction of at least 10 dBA (some use 5 dBA as a minimum). Most states use the FHWA model for highway noise prediction, and two thirds of the states design for the most critical receptor. Systematic procedures to obtain data on impacts on residents and motorists are discussed. The perceived effectiveness is often influenced by aesthetics and landscaping of a barrier rather than by acoustical performance. Maintenance problems of barriers include difficulty with mowing close to barriers, litter accumulation, graffiti, and vandalism. Several states have developed priority rating systems for installing noise barriers on existing highways. Design details as well as construction and maintenance aspects are covered in this report. It is recommended that states seek innovative ways to reduce mass of barriers while maintaining noise reduction capability.

**Verdict:** _____

---

##  64. [W98538216](https://openalex.org/W98538216) — 1986 — article — `pre1990`

**Concepts:** Accreditation (0.60), Acceptance testing (0.56), Computer science (0.46), Reliability engineering (0.41), Medical physics (0.35)

**Title:** Technical evaluation of draft ANSI Standard N13. 30, ''performance criteria for radiobioassay''

> The Pacific Northwest Laboratory (PNL) is conducting a research program to evaluate the appropriateness of criteria in the ANSI draft Standard N13.30, ''Performance Criteria for Radiobioassay.'' The evaluation has progressed parallel with the preparation of the Standard by evaluating the performance of existing bioassay laboratories against the criteria specified. Recommendations for revision of the Standard and implementation of a testing/accreditation program have been formulated based on study results. The current performance testing program includes both in-vivo counting and in-vitro sample measurements. Test criteria specified in the Standard include relative bias, relative precision, and acceptable minimum detectable activity (AMDA). Results to date have indicated that the acceptance criteria in the Standard are appropriate for the existing state of the industry and are achievable by a majority of the participating laboratories. Specific conclusions are that the AMDA criteria are most difficult for the laboratories to achieve; the relative bias criterion is second in difficulty, and the precision criterion presents no problem for the laboratories; most of the participating laboratories can meet the Standard; and failure rates may decrease as the laboratories become more knowledgeable of the performance criteria. 3 refs., 11 figs., 6 tabs.

**Verdict:** _____

---

##  65. [W179519192](https://openalex.org/W179519192) — 1963 — article — `pre1990`

**Concepts:** Mass spectrometry (0.75), Molecular beam (0.70), Spectrometer (0.66), Amplifier (0.59), Beam (structure) (0.55)

**Title:** ANALYTICAL MASS SPECTROMETER WITH MODULATED MOLECULAR BEAM

> A mass spectrometer for the analysis of a gas in the form of a molecular beam is described. The apparatus was developed on the basis of the mass spectrometer MS-2M. In the system the formation and modulation of the molecular beam were accomplished directly in the ion source. For measuring the ion current and electronic multiplier was used and the output was switched into an amplifier and a phase-sensitive detector. The sensitivity of the apparatus in the absence of background was 10/sup -3/% but 10/sup -2/% in the presence of background. Use of a modulated beam reduced the background by an order of magnitude. (tr-auth)

**Verdict:** _____

---

##  66. [W2316946868](https://openalex.org/W2316946868) — 1954 — article — `pre1990`

**Concepts:** Wallerian degeneration (0.67), Icon (0.64), Citation (0.63), Library science (0.48), Information retrieval (0.45)

**Title:** Chemical studies of peripheral nerve during Wallerian degeneration. 6. Incorporation of radioactive phosphate into pentosenucleic acid and phospholipin <i>in vitro</i>

> Research Article| October 01 1954 Chemical studies of peripheral nerve during Wallerian degeneration. 6. Incorporation of radioactive phosphate into pentosenucleic acid and phospholipin in vitro W. L. Magee; W. L. Magee 1Department of Biochemistry, University of Western Ontario, London, Canada Search for other works by this author on: This Site PubMed Google Scholar R. J. Rossiter R. J. Rossiter 1Department of Biochemistry, University of Western Ontario, London, Canada Search for other works by this author on: This Site PubMed Google Scholar Author and article information Publisher: Portland Press Ltd © 1954 CAMBRIDGE UNIVERSITY PRESS1954 Biochem J (1954) 58 (2): 243–249. https://doi.org/10.1042/bj0580243 Views Icon Views Article contents Figures & tables Video Audio Supplementary Data Peer Review Share Icon Share Facebook Twitter LinkedIn Email Cite Icon Cite Get Permissions Citation W. L. Magee, R. J. Rossiter; Chemical studies of peripheral nerve during Wallerian degeneration. 6. Incorporation of radioactive phosphate into pentosenucleic acid and phospholipin in vitro. Biochem J 1 October 1954; 58 (2): 243–249. doi: https://doi.org/10.1042/bj0580243 Download citation file: Ris (Zotero) Reference Manager EasyBib Bookends Mendeley Papers EndNote RefWorks BibTex toolbar search Search Dropdown Menu toolbar search search input Search input auto suggest filter your search All ContentAll JournalsBiochemical Journal Search Advanced Search This content is only available as a PDF. © 1954 CAMBRIDGE UNIVERSITY PRESS1954 Article PDF first page preview Close Modal You do not currently have access to this content.

**Verdict:** _____

---

##  67. [W1481809268](https://openalex.org/W1481809268) — 1982 — article — `pre1990`

**Concepts:** Respite care (0.71), Transport engineering (0.64), Intrusion (0.52), Control (management) (0.50), Traffic volume (0.45)

**Title:** Controlling vehicle speeds on local streets

> Engineers and planners have realised that traffic volume is not the only component of traffic intrusion problems in residential areas; rather these problems are multi-dimensional. Vehicle speed is one of these additional dimensions. Residents have also demonstrated an unwillingness to greatly sacrifice their personal mobility to gain respite from traffic intrusion. Thus there has been a shift in local area planning from measures such as street closures to the use of devices for speed control (e. g. humps, narrowings, chicanes and roundabouts), and the imposition of special speed limits. This note provides some initial steps towards the formal definition of local area traffic planning objectives, and introduces some possible mathematical models. Language: en

**Verdict:** _____

---

##  68. [W2048608413](https://openalex.org/W2048608413) — 1964 — article — `pre1990`

**Concepts:** Newton's laws of motion (0.88), Law (0.66), Physics (0.64), Impulse (physics) (0.63), Interpretation (philosophy) (0.52)

**Title:** Newton's Laws of Motion and the 17th Century Laws of Impact

> A number of writers on history of science have made it clear that in using the term “motive force” in the “Principia,” Newton referred to what we now call “impulse.” With this interpretation, there is a simple and plausible connection between the laws of impact as they were known and described in Newton's day and Newton's formulation of the Laws of Motion in the “Principia,” and we speculate that Newton might have been motivated by such a perception.

**Verdict:** _____

---

##  69. [W1999634748](https://openalex.org/W1999634748) — 1929 — article — `pre1990`

**Concepts:** Colles' fracture (0.85), Orthodontics (0.44), Computer science (0.37), Medicine (0.34), Anatomy (0.23)

**Title:** AN INVESTIGATION OF THE END-RESULTS OF COLLES'S FRACTURES

> THE following account is based on the examination of about 50 cases of Colles's fracture sustained at least two years previous to our examiniation, in an endeavour to ascertain the causes for the imperfect results that obtain from the ustial methods of treatment at present adopted. Our investigation was made on different lines from those of Edwards and Clayton, whose interesting analysis of 424 fractures of the lower end of the radius in adults appeers in the British MIedical Journal for January 12th (p. 61), but we feel that this account may be of value, particularly when compared with theirs.

**Verdict:** _____

---

##  70. [W4238485385](https://openalex.org/W4238485385) — 1938 — article — `pre1990`

**Concepts:** Pseudonym (1.00), Volume (thermodynamics) (0.57), Art (0.43), Computer science (0.38), Art history (0.37)

**Title:** “Adeline”: Pseudonym

> “Adeline”: Pseudonym Get access A. Mary Kirkus A. Mary Kirkus Search for other works by this author on: Oxford Academic Google Scholar Notes and Queries, Volume 175, Issue 25, 17 December 1938, Page 445, https://doi.org/10.1093/nq/175.25.445d Published: 17 December 1938

**Verdict:** _____

---

##  71. [W2334629302](https://openalex.org/W2334629302) — 1959 — article — `pre1990`

**Concepts:** Acoustics (0.35), Physics (0.34)

**Title:** Fields in electrically short ground systems: an experimental study

> An experimental study of m agnetic fi eld di stribu tion in a simplifi cd radial g round system on poorly conducting soil unde r an electri cally short, top loaded monopolc is d escribed.

**Verdict:** _____

---

##  72. [W1991397619](https://openalex.org/W1991397619) — 1988 — article — `pre1990`

**Concepts:** Publishing (0.66), Library science (0.39), Computer science (0.39), Operations research (0.38), Management (0.32)

**Title:** Artificial Intelligence by Patrick Henry Winston (second edition) Addison-Wesley Publishing Company, Massachusetts, USA, July 1984 (£18.95, student hardback edition)

> An abstract is not available for this content so a preview has been provided. Please use the Get access link above for information on how to access this content.

**Verdict:** _____

---

##  73. [W1965061636](https://openalex.org/W1965061636) — 1982 — article — `pre1990`

**Concepts:** Diagrammatic reasoning (0.66), Unitary group (0.53), Factorization (0.50), Algebra over a field (0.49), Basis (linear algebra) (0.49)

**Title:** Matrix element factorization in the unitary group approach for configuration interaction calculations

> Abstract Techniques of diagrammatic spin algebra are employed to derive segment factorization formulas for spin‐adapted matrix elements of one‐ and two‐electron excitation operators. The spin‐adapted basis is formed by the Yamanouchi–;Kotani geneological coupling method, and therefore constitutes an irreducible basis of the unitary group U ( N ), as prescribed by Gel'fand and Tsetlin. Several features distinguish this paper from similar work that has recently been published. First, intermediate steps in the derivation of each segment factor are fully documented. Comprehensive tables list the spin diagrams and phases that contribute to the possible segment factors. Second, a special effort has been made to distinguish between those parts of a segment factor that can be ascribed to a spin diagram and those parts which arise from the orbitals. The results of this paper should thus be useful for those who wish to extend diagrammatic spin algebra to evaluation of matrix elements for states built from nonorthogonal orbitals. Third, a novel graphical method has been introduced to keep track of phase changes that are induced by line up permutations of creation and annihilation operators. This technique may be useful for extension of our analysis to higher excitations. The necessary concepts of second quantization and diagrammatic spin algebra are developed in situ , so the present derivation should be accessible to those who have little prior knowledge of such methods.

**Verdict:** _____

---

##  74. [W2086792063](https://openalex.org/W2086792063) — 1988 — article — `pre1990`

**Concepts:** Ground reaction force (0.80), Weighting (0.73), Symmetry (geometry) (0.71), Amplitude (0.62), Mathematics (0.49)

**Title:** The use of H(orse) INDEX: A method of analysing the ground reaction force patterns of lame and normal gaited horses at the walk

> The amplitudes, impulses and times of occurrence of a number of selected peaks in the ground reaction force tracings of 17 horses with various clinical histories were compared with those of 20 horses used to establish values for the 'standard' Dutch Warmblood horse. The resulting factors were combined, using different weighting factors, into indices characterising each limb. The symmetry between the loading of the forelimbs and the hindlimbs was used to calculate amplitude and peak-time symmetry indices. Limb and symmetry indices were combined in one H(orse) INDEX. This method of quantifying the ground reaction force pattern, together with appropriate graphic display of the tracings, was useful in clinical evaluation of force plate measurements.

**Verdict:** _____

---

##  75. [W1539568082](https://openalex.org/W1539568082) — 1976 — article — `pre1990`

**Concepts:** Algorithm (0.65), Annotation (0.54), Computer science (0.49), Artificial intelligence (0.45), Type (biology) (0.42)

**Title:** Some special decompositions of 𝐸³

> A great deal of attention has been given to the question: which upper semicontinuous decompositions of <inline-formula content-type="math/mathml"> <mml:math xmlns:mml="http://www.w3.org/1998/Math/MathML" alttext="upper E cubed"> <mml:semantics> <mml:mrow class="MJX-TeXAtom-ORD"> <mml:msup> <mml:mi>E</mml:mi> <mml:mn>3</mml:mn> </mml:msup> </mml:mrow> <mml:annotation encoding="application/x-tex">{E^3}</mml:annotation> </mml:semantics> </mml:math> </inline-formula> into pointlike continua give <inline-formula content-type="math/mathml"> <mml:math xmlns:mml="http://www.w3.org/1998/Math/MathML" alttext="upper E cubed"> <mml:semantics> <mml:mrow class="MJX-TeXAtom-ORD"> <mml:msup> <mml:mi>E</mml:mi> <mml:mn>3</mml:mn> </mml:msup> </mml:mrow> <mml:annotation encoding="application/x-tex">{E^3}</mml:annotation> </mml:semantics> </mml:math> </inline-formula>. It has recently been determined that some decompositions of <inline-formula content-type="math/mathml"> <mml:math xmlns:mml="http://www.w3.org/1998/Math/MathML" alttext="upper E cubed"> <mml:semantics> <mml:mrow class="MJX-TeXAtom-ORD"> <mml:msup> <mml:mi>E</mml:mi> <mml:mn>3</mml:mn> </mml:msup> </mml:mrow> <mml:annotation encoding="application/x-tex">{E^3}</mml:annotation> </mml:semantics> </mml:math> </inline-formula> into points and straight line segments give decomposition spaces which are topologically distinct from <inline-formula content-type="math/mathml"> <mml:math xmlns:mml="http://www.w3.org/1998/Math/MathML" alttext="upper E cubed"> <mml:semantics> <mml:mrow class="MJX-TeXAtom-ORD"> <mml:msup> <mml:mi>E</mml:mi> <mml:mn>3</mml:mn> </mml:msup> </mml:mrow> <mml:annotation encoding="application/x-tex">{E^3}</mml:annotation> </mml:semantics> </mml:math> </inline-formula>. In this paper we apply a new condition to the set of nondegenerate elements of a decomposition which enables one to conclude that the resulting decomposition space is homeomorphic to <inline-formula content-type="math/mathml"> <mml:math xmlns:mml="http://www.w3.org/1998/Math/MathML" alttext="upper E cubed"> <mml:semantics> <mml:mrow class="MJX-TeXAtom-ORD"> <mml:msup> <mml:mi>E</mml:mi> <mml:mn>3</mml:mn> </mml:msup> </mml:mrow> <mml:annotation encoding="application/x-tex">{E^3}</mml:annotation> </mml:semantics> </mml:math> </inline-formula>.

**Verdict:** _____

---

##  76. [W1146618898](https://openalex.org/W1146618898) — 1989 — article — `pre1990`

**Concepts:** Mile (0.74), Environmental science (0.59), Nuclear engineering (0.57), Core (optical fiber) (0.53), Nuclear reactor core (0.52)

**Title:** Three Mile Island Unit 2 Preparations for Defueling

> The accident at Three Mile Island Unit 2 left the reactor core in a severely degraded condition. Core removal methods and equipment designed for an undamaged reactor refueling required extensive modification. Fuel debris containments, tooling, contamination control, and water processing methods were tailored to known and postulated core conditions using primarily manual rather than robotic methods. Flexibility was a key element in the equipment design since little definitive data on reactor physical conditions were available.

**Verdict:** _____

---

##  77. [W3101340392](https://openalex.org/W3101340392) — 1958 — article — `pre1990`

**Concepts:** Humanities (0.49), Political science (0.42), Physics (0.34), Art (0.28)

**Title:** Integração dos transportes ferroviários suburbanos no sistema geral de viação do Distrito Federal

> A rigor, na pesquisa de soluções para os problemas dos transportes cole»tivos do Distrito Federal, não se pode, por meras questões teóricas,ignorar pura e simplesmente a existência dos serviços suburbanos m antidospelas estradas de ferro, pôstc que as quatro rêdes ferroviárias locais ocupam,e ocuparão sempre, posição privilegiada ao longo de consideráveis concentrações demográficas da cidade, como eixos naturais que são do sistemade transportes coletivos das mesmas.

**Verdict:** _____

---

##  78. [W4233978712](https://openalex.org/W4233978712) — 1987 — report — `pre1990`

**Concepts:** Physics (0.90), Hadron (0.69), Pion (0.68), Annihilation (0.56), Particle physics (0.43)

**Title:** Bose-Einstein correlations in e/sup +/e/sup -/ collisions

> The MARK II detector is used to study the Bose-Einstein correlation between pairs and triplets of charged pions produced in hadronic decays of the J)psi), the ..sqrt..s = 4 to 7 GeV continuum above the J)psi), two photon events at ..sqrt..s = 29 GeV, and e/sup )plus/)e/sup )minus/) annihilation events at ..sqrt..s = 29 GeV as a function of Q/sup 2/, the four-momentum transfer squared. After corrections for Coulomb effects and pion misidentification, we find a nearly full Bose-Einstein enhancement ..cap alpha.. in the J)psi) and the two photon data and about half the maximum value in the other two data sets. The radius parameter )tau)(an average over space and time) given by pion pair analyses lies within a band of +-0.10 fm around 0.73 fm and is the same, within errors, for all four data sets. Pion triplet analyses also give a consistent radius of approx. 0.54 fm. fits to two-dimensional distributions R(q/sub T//sup 2/, q/sub C//sup 2/) of invariant components of Q/sup 2/ = q/sub T//sup 2/ )plus) q/sub C//sup 2/ give )tau)/sub T/ approx. )tau)C approx. )tau), where q/sub T/ is the transverse three-momentum difference calculated with respect to the net pair three-momentum, and q/sub C/ is in effect the longitudinal three-momentum difference in the pion pair rest frame. When q/sub T/ is calculated with respect to the jet axis for two-jet events in the e/sup )plus/)e/sup )minus/) annihilation data at ..sqrt..s = 29 GeV, a fit to R(q/sub T//sup 2/, q/sub C//sup 2/) also gives )tau)/sub T/ approx. )tau)/sub C/ approx. )tau). Noting that q/sub L/ and q/sub 0/ are not invariant, we make fits to R(/sub T//sup T/, q/sub L//sup 2/) and to R(q/sub T//sup 2/, q/sub 0//sup 2/) (Kopylov formulation), and we find )tau)/sub 0/ approx. )tau)/sub L/ approx. )23))tau)/sub T/ to )12))tau)/sub T/. 44 refs., 43 figs., 15 tabs

**Verdict:** _____

---

##  79. [W754692244](https://openalex.org/W754692244) — 1978 — book — `pre1990`

**Concepts:** Plan (archaeology) (0.49), Computer science (0.34), Geography (0.23), Archaeology (0.07)

**Title:** Clatskanie : Comprehensive plan (1978)

> 86 pp. Bookmarks supplied by UO. Map, charts. Published July, 1978. Scanned by UO from item HT168 .C53 S54 1978, May, 2009.

**Verdict:** _____

---

##  80. [W4235559521](https://openalex.org/W4235559521) — 1972 — dissertation — `pre1990`

**Concepts:** Nonlinear system (0.87), A priori and a posteriori (0.74), Identification (biology) (0.63), Nonlinear system identification (0.61), System identification (0.60)

**Title:** Maximum likelihood identification of nonlinear systems.

> Maximum likelihood technique 1s used to estimate the parameters of single input single output nonlinear systems. Two algorithms are described and applied . One is for the identification of Hammerstein nonlinear models, which is useful if no priori knowledge about the mathematical form of the nonlinearity is available. The other algorithm is for the identification of systems which have known forms for the nonlinearities. It is derived for continuous nonlinear systems, and applied for simulated data generated from linear and nonlinear second order continuous models. It is also used to fit linear, and nonlinear second order continuous models to practical data taken from a test on the glucose homeostatic control system of dogs. The emphasis is on obtaining simplified algorithm for continuous nonlinear systems in order to save computing time, and get satisfactory results.

**Verdict:** _____

---

##  81. [W4210367069](https://openalex.org/W4210367069) — 1955 — article — `pre1990`

**Concepts:** Citation (0.70), Computer science (0.53), Altmetrics (0.46), Social media (0.42), Library science (0.34)

**Title:** GOVERNMENT

> RETURN TO ISSUEPREVNewsNEXTGOVERNMENTRussia's Big BombSoviet explodes megaton nuclear weapon, called "largest thus far" by Atomic Energy CommissionCite this: Chem. Eng. News 1955, 33, 49, 5264Publication Date (Print):December 5, 1955Publication History Published online5 November 2010Published inissue 5 December 1955https://doi.org/10.1021/cen-v033n049.p5264Copyright © 1955 AMERICAN CHEMICAL SOCIETYArticle Views4Altmetric-Citations-LEARN ABOUT THESE METRICSArticle Views are the COUNTER-compliant sum of full text article downloads since November 2008 (both PDF and HTML) across all institutions and individuals. These metrics are regularly updated to reflect usage leading up to the last few days.Citations are the number of other articles citing this article, calculated by Crossref and updated daily. Find more information about Crossref citation counts.The Altmetric Attention Score is a quantitative measure of the attention that a research article has received online. Clicking on the donut icon will load a page at altmetric.com with additional details about the score and the social media presence for the given article. Find more information on the Altmetric Attention Score and how the score is calculated. Share Add toView InAdd Full Text with ReferenceAdd Description ExportRISCitationCitation and abstractCitation and referencesMore Options Share onFacebookTwitterWechatLinked InReddit PDF (100 KB) SUBJECTS:Energy,Explosives,Quantum mechanics,Uranium Get e-Alerts

**Verdict:** _____

---

##  82. [W119805742](https://openalex.org/W119805742) — 1983 — article — `pre1990`

**Concepts:** Magnetohydrodynamics (0.80), Physics (0.68), Flute (0.62), Dissipative system (0.62), Instability (0.59)

**Title:** Flute instability in an open min B system

> In a confinement system with an average min B, in part of which the particles undergo an unfavorable magnetic drift, the familiar MHD flute waves may be accompanied by some natural flute waves with an azimuthal phase velocity on the order of or smaller than the magnetic drift velocity of the ions in the region of favorable curvature. This wave branch is not described in the MHD approximation; it arises in the two-fluid model. These waves have a negative energy and may thus be excited by dissipative effects.

**Verdict:** _____

---

##  83. [W2789153476](https://openalex.org/W2789153476) — 1934 — article — `pre1990`

**Concepts:** Philosophy (0.65), Humanities (0.62), Physics (0.36)

**Title:** Sensibilitat a les Tuberculines Antiga de Koch i B.C.G. en nens que han ingerit vacuna B.C.G. durant els deu primers dies de la seva vida i permaneixent en un medi suposat indemne

> espanolComparando las reacciones obtenidas para precisar la sensibilidad de - la tuberculina antigua i la tuberculina B. C. G., observan: Que el nino vacunado con B. C. G. por via oral es mas sensible a la tuberculina de este bacilo que a la antigua de Koch ; Que es mayor el numero de reacciones positivas fugaces empleando, tuberculina B. C. G.; Que estas reacciones aumentan al aumentar la concentracion de las soluciones empleadas. Se podria aun anadir, junto con otros'observadores,.que la precocidad y fugacidad de las reacciones son propias de los medios sanos; asi como la persistencia lo es de los medios infectados. francaisEn comparant les reactions obtenues pour preciser la sensibilite de la tuberculine ancienne et la tuberculine B. C. G. il observe : Que l'enfant vaccine avec B. C. G. par voie orale est plus sensible a la tuberculine de ce bacille qu'a, l'encienne de Koch; Que le nombre de reactions fugaces est superieur en employant la tuberculine B. C. G.; Que ces reactions augmentent quand augmente la concentration des solutions employees. On pourrait ajouter, avec les observateurs, que la precocite et fugacite des reactions somit .propres des millieux sains; ainsi que la persistence l'est, des millieus infectes.

**Verdict:** _____

---

##  84. [W2342437579](https://openalex.org/W2342437579) — 1978 — article — `pre1990`

**Concepts:** Computer science (0.65), Vocational education (0.62), Linear programming (0.59), Manpower planning (0.57), Investment (military) (0.57)

**Title:** Models for Educational and Manpower Planning: A Dynamic Linear Programming Approach

> The purpose of this paper is to show that many optimization problems for educational and manpower planning models can be written in a standard dynamic linear programming form. A basic model of educational planning is described and extensions of the model (investment and vocational training submodels and a three level educational model) are given. \n\nWhen describing models, two basic models are singled out using two different controls: recruitment in the first and promotion in the second. Finally, an integrated model of economy-manpower interaction is considered. \n\nThe possibilities and limitations of DLP as applied to manpower and educational planning problems are discussed.

**Verdict:** _____

---

##  85. [W2151004606](https://openalex.org/W2151004606) — 1972 — article — `pre1990`

**Concepts:** Isotropy (0.77), Physics (0.75), Vorticity (0.74), Angular velocity (0.69), Turbulence (0.57)

**Title:** A note on the angular dispersion of a fluid line element in isotropic turbulence

> The mean-square angular displacement of a fluid material line element is expressed as an integral of the corresponding angular velocity in material coordinates, with forms like those in Taylor's (1921) linear displacement analysis. Measurements using a hydrogen-bubble tracer in isotropic turbulence show that the mean-square angular velocity of a line is of the same order of magnitude as the mean-square vorticity, and that its ‘Lagrangian’ integral time scale is of the order of the inverse of the r.m.s. vorticity. The angular velocity of a line element is also formulated in spatial co-ordinates. Finally, the connexion between angular dispersion and the approach toward isotropy is pointed out.

**Verdict:** _____

---

##  86. [W2060959612](https://openalex.org/W2060959612) — 1988 — article — `pre1990`

**Concepts:** Physics (0.70), Mixing (physics) (0.66), Photorefractive effect (0.65), Optics (0.61), Holography (0.60)

**Title:** Anisotropic four-wave mixing in cubic photorefractive crystals

> The anisotropic four-wave mixing in the scheme recently proposed by S.I. Stepanov and M.P. Petrov (Opt. Commun. vol.53, p.64-8, 1985) is studied. The main feature of this interaction arrangement is that the same phase hologram (index grating) has opposite contrasts for orthogonally polarized, counterpropagating waves. The coupled nonlinear equations, in the case of transmission and reflection gratings, for the pi /2 photorefractive phase shift are exactly solved, and their properties are discussed in detail. The numerical evidence of the effects of bistability and self-oscillation is included.< <ETX xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink">&gt;</ETX>

**Verdict:** _____

---

##  87. [W4303078340](https://openalex.org/W4303078340) — 1915 — article — `pre1990`

**Concepts:** Icon (0.97), Citation (0.57), Download (0.54), Information retrieval (0.45), Computer science (0.43)

**Title:** The Belgian Soldier

> Essay| March 01 1915 The Belgian Soldier Current History (1915) 1 (6): 1215–1216. https://doi.org/10.1525/curh.1915.1.6.1215 Views Icon Views Article contents Figures & tables Video Audio Supplementary Data Peer Review Share Icon Share Twitter LinkedIn Tools Icon Tools Get Permissions Cite Icon Cite Search Site Citation The Belgian Soldier. Current History 1 March 1915; 1 (6): 1215–1216. doi: https://doi.org/10.1525/curh.1915.1.6.1215 Download citation file: Ris (Zotero) Reference Manager EasyBib Bookends Mendeley Papers EndNote RefWorks BibTex toolbar search Search Dropdown Menu toolbar search search input Search input auto suggest filter your search All ContentCurrent History Search This content is only available via PDF. © 1915 by The Regents of the University of California1915 Article PDF first page preview Close Modal You do not currently have access to this content.

**Verdict:** _____

---

##  88. [W1654257636](https://openalex.org/W1654257636) — 1973 — article — `pre1990`

**Concepts:** Computer science (0.31)

**Title:** 19世紀イギリス金本位制における国際収支調整メカニズム--A.G.フォードの分析を中心にして

> ? ( 1 ) l l = ( 2 ) () ( 3 ) D 1 9 ( 1 8 8 0 -1 9 1 4 1 9 ) ( 1 ) ( 4 ) ( 2 ) A G F o r d ; The g o l d S t a n d a r d 1 8 8 0 ' " ' -' 1 9 1 4 ; B r i t a i n a n d A r g e n t i n a ) O x f o r d ) 1 9 6 2 4i 7t ( 5 ) O () ( 1 ) A HH a n s e n T h e D o l l a r a n d T h e I n t e r n a t i o n a l M o n e t a r y S y s t e m 1 9 6 5J3 0 -----3 1 ( 2 ) j = () = 1

**Verdict:** _____

---

##  89. [W4251185510](https://openalex.org/W4251185510) — 1958 — article — `pre1990`

**Concepts:** Citation (0.74), Icon (0.72), Altmetrics (0.69), Social media (0.58), Computer science (0.54)

**Title:** Beckman Instruments, Inc.

> ADVERTISEMENT RETURN TO ISSUEPREVArticleNEXTBeckman Instruments, Inc.Cite this: Anal. Chem. 1958, 30, 9, 38APublication Date (Print):September 1, 1958Publication History Published online16 May 2012Published inissue 1 September 1958https://doi.org/10.1021/ac60141a731RIGHTS & PERMISSIONSArticle Views6Altmetric-Citations-LEARN ABOUT THESE METRICSArticle Views are the COUNTER-compliant sum of full text article downloads since November 2008 (both PDF and HTML) across all institutions and individuals. These metrics are regularly updated to reflect usage leading up to the last few days.Citations are the number of other articles citing this article, calculated by Crossref and updated daily. Find more information about Crossref citation counts.The Altmetric Attention Score is a quantitative measure of the attention that a research article has received online. Clicking on the donut icon will load a page at altmetric.com with additional details about the score and the social media presence for the given article. Find more information on the Altmetric Attention Score and how the score is calculated. Share Add toView InAdd Full Text with ReferenceAdd Description ExportRISCitationCitation and abstractCitation and referencesMore Options Share onFacebookTwitterWechatLinked InReddit PDF (685 KB) Get e-Alerts Get e-Alerts

**Verdict:** _____

---

##  90. [W2571345580](https://openalex.org/W2571345580) — 1983 — article — `pre1990`

**Concepts:** Physics (0.88), Planetary nebula (0.76), Astrophysics (0.69), Photometry (optics) (0.57), Astronomy (0.50)

**Title:** Two-dimensional photometry of planetary nebulae

> In connection with the study of planetary nebulae, problems still exist in understanding such basic properties as three-dimensional structure, optical opacity to the central star's ionizing flux, and electron temperature and electron density variations within the nebular gas. To study these properties, two-dimensional images taken in many spectral lines are required. However, such a study presents a formidable problem in data analysis. In the present investigation, an attempt has been made to overcome the difficulties by using an imaging system which encodes the data digitally. Calibrated intensity maps could be constructed to test models of ionization structure and to produce two-dimensional maps of electron temperature and density. Both the results of a uniform-shell test and the nature of the solutions for the volume emissivity were found to support a nebular model in which the bright ring is part of a closed shell of variable density that resembles the torus proposed by Minkowski and Osterbrock (1960).

**Verdict:** _____

---

##  91. [W1643224738](https://openalex.org/W1643224738) — 1988 — article — `pre1990`

**Concepts:** Traveling-wave tube (0.90), Tube (container) (0.61), Electron gun (0.59), Magnet (0.53), Cathode ray (0.52)

**Title:** Development of a 75-watt 60-GHz traveling-wave tube for intersatellite communications

> This program covers the initial design and development of a 75 watt, 60 GHz traveling-wave tube for intersatellite communications. The objective frequency band was 59 to 64 GHz, with a minimum tube gain of 35 dB. The objective overall efficiency at saturation was 40 percent. The tube, designated the 961H, used a coupled-cavity interaction circuit with periodic permanent magnet beam focusing to minimize the weight. For efficiency enhancement, it incorporated a four-stage depressed collector capable of radiation cooling in space. The electron gun had a low-temperature (type-M) cathode and an isolated anode. Two tubes were built and tested; one feasibility model with a single-stage collector and one experimental model that incorporated the multistage collector.

**Verdict:** _____

---

##  92. [W4236249224](https://openalex.org/W4236249224) — 1987 — article — `pre1990`

**Concepts:** Citation (0.73), Altmetrics (0.71), Icon (0.65), Social media (0.60), Computer science (0.57)

**Title:** NEW PRODUCTS

> ADVERTISEMENT RETURN TO ISSUEPREVArticleNEXTNEW PRODUCTSCite this: Anal. Chem. 1987, 59, 4, 352APublication Date (Print):February 15, 1987Publication History Published online30 May 2012Published inissue 15 February 1987https://doi.org/10.1021/ac00131a751RIGHTS & PERMISSIONSArticle Views9Altmetric-Citations-LEARN ABOUT THESE METRICSArticle Views are the COUNTER-compliant sum of full text article downloads since November 2008 (both PDF and HTML) across all institutions and individuals. These metrics are regularly updated to reflect usage leading up to the last few days.Citations are the number of other articles citing this article, calculated by Crossref and updated daily. Find more information about Crossref citation counts.The Altmetric Attention Score is a quantitative measure of the attention that a research article has received online. Clicking on the donut icon will load a page at altmetric.com with additional details about the score and the social media presence for the given article. Find more information on the Altmetric Attention Score and how the score is calculated. Share Add toView InAdd Full Text with ReferenceAdd Description ExportRISCitationCitation and abstractCitation and referencesMore Options Share onFacebookTwitterWechatLinked InReddit PDF (805 KB) Get e-Alerts Get e-Alerts

**Verdict:** _____

---

##  93. [W2040936722](https://openalex.org/W2040936722) — 1974 — article — `pre1990`

**Concepts:** Citation (0.70), Icon (0.57), Altmetrics (0.47), Social media (0.46), Computer science (0.45)

**Title:** Aliphatic semidiones. XXIV. Bicyclo[n.2.0]alkane-2,3-semidiones

> ADVERTISEMENT RETURN TO ISSUEPREVArticleNEXTAliphatic semidiones. XXIV. Bicyclo[n.2.0]alkane-2,3-semidionesGlen A. Russell, Philip R. Whittle, C. S. C. Chung, Y. Kosugi, Kirk Schmitt, and Edward GoettertCite this: J. Am. Chem. Soc. 1974, 96, 22, 7053–7057Publication Date (Print):October 1, 1974Publication History Published online1 May 2002Published inissue 1 October 1974https://pubs.acs.org/doi/10.1021/ja00829a037https://doi.org/10.1021/ja00829a037research-articleACS PublicationsRequest reuse permissionsArticle Views56Altmetric-Citations10LEARN ABOUT THESE METRICSArticle Views are the COUNTER-compliant sum of full text article downloads since November 2008 (both PDF and HTML) across all institutions and individuals. These metrics are regularly updated to reflect usage leading up to the last few days.Citations are the number of other articles citing this article, calculated by Crossref and updated daily. Find more information about Crossref citation counts.The Altmetric Attention Score is a quantitative measure of the attention that a research article has received online. Clicking on the donut icon will load a page at altmetric.com with additional details about the score and the social media presence for the given article. Find more information on the Altmetric Attention Score and how the score is calculated. Share Add toView InAdd Full Text with ReferenceAdd Description ExportRISCitationCitation and abstractCitation and referencesMore Options Share onFacebookTwitterWechatLinked InRedditEmail Other access optionsGet e-Alertsclose Get e-Alerts

**Verdict:** _____

---

##  94. [W2061271773](https://openalex.org/W2061271773) — 1969 — article — `pre1990`

**Concepts:** Citation (0.65), Altmetrics (0.64), Potentiometric titration (0.64), Icon (0.48), Titration (0.47)

**Title:** Potentiometric titration of stereoregular poly(acrylic acids)

> ADVERTISEMENT RETURN TO ISSUEPREVArticleNEXTPotentiometric titration of stereoregular poly(acrylic acids)Yoshikazu Kawaguchi and Mitsuru NagasawaCite this: J. Phys. Chem. 1969, 73, 12, 4382–4384Publication Date (Print):December 1, 1969Publication History Published online1 May 2002Published inissue 1 December 1969https://pubs.acs.org/doi/10.1021/j100846a065https://doi.org/10.1021/j100846a065research-articleACS PublicationsRequest reuse permissionsArticle Views271Altmetric-Citations29LEARN ABOUT THESE METRICSArticle Views are the COUNTER-compliant sum of full text article downloads since November 2008 (both PDF and HTML) across all institutions and individuals. These metrics are regularly updated to reflect usage leading up to the last few days.Citations are the number of other articles citing this article, calculated by Crossref and updated daily. Find more information about Crossref citation counts.The Altmetric Attention Score is a quantitative measure of the attention that a research article has received online. Clicking on the donut icon will load a page at altmetric.com with additional details about the score and the social media presence for the given article. Find more information on the Altmetric Attention Score and how the score is calculated. Share Add toView InAdd Full Text with ReferenceAdd Description ExportRISCitationCitation and abstractCitation and referencesMore Options Share onFacebookTwitterWechatLinked InRedditEmail Other access options Get e-Alerts

**Verdict:** _____

---

##  95. [W335550946](https://openalex.org/W335550946) — 1979 — report — `pre1990`

**Concepts:** Compatibility (geochemistry) (0.72), Computer science (0.38), Materials science (0.35), Composite material (0.10)

**Title:** Investigation of Ties and Adaptive Antenna Technology Compatibility.

> Abstract : TIES(Tactical Information Exchange System) is being developed by the Navy to provide a new architecture for airborne CNI (communication, navigation and identification). An adaptive array (AA) can provide jam resistance to CNI receivers by spatially nulling interferences. The results of an investigation of the compatibility of AA processing within the TIES are presented. Candidate implementation schemes are examined for the TIES-AA. (Author)

**Verdict:** _____

---

##  96. [W4312760180](https://openalex.org/W4312760180) — 1985 — article — `pre1990`

**Concepts:** Icon (0.87), Citation (0.71), Download (0.67), Publishing (0.44), History (0.43)

**Title:** The Old Folks Day: A Unique Utah Tradition

> Research Article| April 01 1985 The Old Folks Day: A Unique Utah Tradition JOSEPH HEINERMAN JOSEPH HEINERMAN Search for other works by this author on: This Site Google Utah Historical Quarterly (1985) 53 (2): 157–169. https://doi.org/10.2307/45061206 Cite Icon Cite Share Icon Share Facebook Twitter LinkedIn MailTo Permissions Search Site Citation JOSEPH HEINERMAN; The Old Folks Day: A Unique Utah Tradition. Utah Historical Quarterly 1 January 1985; 53 (2): 157–169. doi: https://doi.org/10.2307/45061206 Download citation file: Zotero Reference Manager EasyBib Bookends Mendeley Papers EndNote RefWorks BibTex toolbar search Search Dropdown Menu toolbar search search input Search input auto suggest filter your search All Scholarly Publishing CollectiveUniversity of Illinois PressUtah Historical Quarterly Search Advanced Search The text of this article is only available as a PDF. © Copyright 1985 Utah State Historical Society1985 Article PDF first page preview Close Modal You do not currently have access to this content.

**Verdict:** _____

---

##  97. [W160089336](https://openalex.org/W160089336) — 1975 — article — `pre1990`

**Concepts:** Sampling (signal processing) (0.77), Computer science (0.58), Quality (philosophy) (0.56), Process (computing) (0.54), Simple random sample (0.51)

**Title:** Sampling from Batches

> The outputs of many manufacturing processes consist of batches which tend to be more homogeneous than the outputs from the process as a whole. Thus the quality of just one batch is not necessarily representative of the long term quality of the process. This paper discusses a two stage plan for obtaining representative samples of the outputs of such manufacturing processes. The two stage plan is both more efficient and more convenient than simple random sampling. The plan entails sampling k of the batches and subsampling m units within each of the sampled batches. Formulas are presented which determine how k and m should be chosen to maximize the sampling precision subject to cost constraints. Several numerical examples illustrate the adverse effect on precision due to sampling from too few batches. In particular it is shown that drawing the entire sample from just one batch leads to very poor precision.

**Verdict:** _____

---

##  98. [W2046099298](https://openalex.org/W2046099298) — 1955 — article — `pre1990`

**Concepts:** Citation (0.75), Altmetrics (0.75), Computer science (0.59), Icon (0.58), Social media (0.53)

**Title:** Dehydration of Orthophosphoric Acid

> ADVERTISEMENT RETURN TO ISSUEPREVArticleNEXTDehydration of Orthophosphoric AcidC. E. Higgins and W. H. BaldwinCite this: Anal. Chem. 1955, 27, 11, 1780–1783Publication Date (Print):November 1, 1955Publication History Published online1 May 2002Published inissue 1 November 1955https://pubs.acs.org/doi/10.1021/ac60107a030https://doi.org/10.1021/ac60107a030research-articleACS PublicationsRequest reuse permissionsArticle Views562Altmetric-Citations31LEARN ABOUT THESE METRICSArticle Views are the COUNTER-compliant sum of full text article downloads since November 2008 (both PDF and HTML) across all institutions and individuals. These metrics are regularly updated to reflect usage leading up to the last few days.Citations are the number of other articles citing this article, calculated by Crossref and updated daily. Find more information about Crossref citation counts.The Altmetric Attention Score is a quantitative measure of the attention that a research article has received online. Clicking on the donut icon will load a page at altmetric.com with additional details about the score and the social media presence for the given article. Find more information on the Altmetric Attention Score and how the score is calculated. Share Add toView InAdd Full Text with ReferenceAdd Description ExportRISCitationCitation and abstractCitation and referencesMore Options Share onFacebookTwitterWechatLinked InRedditEmail Other access optionsGet e-Alertsclose Get e-Alerts

**Verdict:** _____

---

##  99. [W2767151332](https://openalex.org/W2767151332) — 1983 — article — `pre1990`

**Concepts:** Computer science (0.45), Engineering (0.42), Engineering drawing (0.41), Mechanical engineering (0.40), Automotive engineering (0.38)

**Title:** Design And Calculation Methods For High-Speed Gears Of Advanced Technology.

> High-speed gears of very high powers and/or very high speeds must be exactly analyzed and optimized in gearing, bearing and housing in order to achieve low noise, low vibra tion running with maximum safety in operation.The gearing must be checked by detailed calculations in load capacity, including an exact analysis of the scoring safety.Special design means must be applied in order to cover thermal problems at the gearing.Besides this, the calculation and design of the plain bear ings are of main interest.They also must be analyzed in detail, not only in general hydrodynamic load capacity, but also in their real temperature and pressure conditions in the oil film.The design of the plain bearing then has to be adapted to its vibration behaviour.Using modern CAE methods, the design process can be made faster and safer.Practical examples of some of the highest-powered high-speed gears of the world prove the methods used in design, calculations and manufacturii).g.

**Verdict:** _____

---

## 100. [W4242422561](https://openalex.org/W4242422561) — 1967 — article — `pre1990`

**Concepts:** Vibration (0.79), Impulse (physics) (0.59), Natural frequency (0.50), Femur (0.50), Acoustics (0.44)

**Title:** On a Bone-Vibration

> This experiment is one step to clarify dynamic mechanical properties of bones, especially femurs.Material: four dry femurs.We designed a method that a mechanical impulse was exerted on a femoral head along the functional axis of femur with a pendulum. Then a femur, whose condyle is fixed and head is free, is placed horizontally.When a mechanical impulse was exerted on a femur in the above position, a bone vibration was developed. This vibration was analyzed, and was similar to a summation of a high- and a low-frequency component. Therefore, we picked out separately the high- and the low-frequency component with a filter circuit. There were vibrations with logarithmic decrement. The vibrations had a natural frequency themselves—the high was about 500cps and the low was about 100cps.Now, a solution of a sort of a second-order differential equation Md2x/dt2+Sdx/dt+Kx=F(t)is also a damping vibration with logarithmic decrement. Then, we added two second-order differential equations with two different constant coefficients, using a desk-top ANALOG computor. Using this solution yielded a similar wave to a bone vibration.Therefore, we think now that a bone vibration under the above conditions may be expressed as a summation of two ordinary second-order differential equations.Furthermore, analysing many more bone-vibrations, we will compare the difference of the damping ratio and the natural frequency of vibration between many bones.

**Verdict:** _____

---
