# Phase 1.2 H2 hand audit — sheet

Generated: 100 papers from `section0-sample-1M-v3.parquet`, stratified 50 uniform + 50 pre-1990. Audit seed: `ws2-phase-1.2-h2-audit-seed-v1`.

## Reviewer task

For each of the 100 papers below, decide whether §0 was right to include it. Write one verdict on the `**Verdict:** _____` line:

- **`OK`** — clearly a research paper in cs or physics with a real abstract. No further note needed.
- **`FLAG: WRONG_FIELD`** — paper is primarily about something else (e.g., chemistry, marketing, biology) and only got tagged as cs/physics because of one or two boilerplate keywords. Add a short reason.
- **`FLAG: BAD_ABSTRACT`** — the abstract is publisher boilerplate (citation menu, icon labels, download buttons), OCR fragments, a stub like "Abstract not available," or otherwise unusable as a representation of the paper's content.
- **`FLAG: JUNK_YEAR`** — pre-1990 paper that contains a post-2000 token the regex missed (e.g., "ChatGPT", "blockchain", "transformer architecture"). Note the specific token.
- **`FLAG: BORDERLINE`** — you're not sure; note why.

**Three things to know going in:**

1. The pass criterion of "0 FLAGs" is aspirational. We expect some FLAGs — the goal is to characterize which patterns of §0 false positives are common, not to certify perfection.
2. Multi-field papers (e.g., a real cs paper that also has bio concepts) are **OK**. The test is whether the paper genuinely belongs in a cs/physics analytical population, not whether cs/physics is its only or primary field. **Important:** "belongs in" means the paper itself (title + abstract) uses cs/physics methods, ideas, or systems — not just that a cs/physics concept appears in the concept list. Every paper in this sample has at least one cs/physics concept ≥0.30 by construction (that's how it got into the sample); seeing one in the list is not on its own evidence of fit. Example: a Croatian urban-planning paper that uses LiDAR + SLAM + 3D point clouds is **OK** (cs methods doing the work); an education-research paper with `computer science (0.34)` tagged but no cs content in the abstract is **WRONG_FIELD** (the tag is concept-tagger noise).
3. If you start seeing the same FLAG pattern repeat (3+ instances of the same root cause), you can stop reviewing the rest of that pattern's likely cases and just note "pattern X seen ≥3 times; recommend filter Y." We're after kinds of error, not a complete enumeration.

---

##   1. [W1979542926](https://openalex.org/W1979542926) — 1993 — article — `uniform`

**Concepts:** Amplitude (0.79), Electroencephalography (0.60), Non-rapid eye movement sleep (0.55), Spectral density (0.51), Amplitude modulation (0.48)

**Title:** Period‐amplitude analysis and power spectral analysis: a comparison based on all‐night sleep EEG recordings

> Both period-amplitude analysis (PAA) and power spectral analysis (PSA) were performed on all-night human sleep EEG recordings obtained from 11 subjects. The comparison of the two methods was based on the PAA variables time in band (a wave incidence measure) and rectified amplitude, and on the PSA variables spectral power density and spectral amplitude (the square root of power). The mean time course of these variables was determined for the first 4 nonREM-REM sleep cycles. Spectral power density and spectral amplitude in the delta range were high in nonREM sleep and low in REM sleep, and showed a declining trend over consecutive nonREM sleep episodes. In the frequency range below 2 Hz, rectified amplitude was highly correlated with both time in band and spectral amplitude, and there was no evidence for a dissociation between wave amplitude and wave incidence measures. However, in frequencies above 2 Hz, the modulation of time in band was a mirror image of that below 2 Hz. This result does not reflect a property of the data, but is inherent to the methodology applied. The reversal point of modulation was merely shifted when the high-pass filter settings were changed. It is concluded that band-pass filtering is necessary prior to PAA even for the analysis of the lowest frequency range, and that the indiscriminate use of PAA may give rise to spurious results.

**Verdict:** FLAG: BORDERLINE (more of an EE paper applied to sleep but passable)

---

##   2. [W2086808546](https://openalex.org/W2086808546) — 2014 — article — `uniform`

**Concepts:** Prioritization (0.78), Probabilistic logic (0.72), Computer science (0.70), Scheme (mathematics) (0.66), Scheduling (production processes) (0.57)

**Title:** Efficient Channel Utilization and Prioritization Scheme for Emergency Calls in Cellular Network

> Handling of emergency calls in wireless cellular networks is one of the major issues. The main objective here is to improve quality of service by efficient channel utilization. In this paper, a new scheme called probabilistic emergency prioritization scheme (PEPS) is proposed which provides highest priority for emergency calls. The proposed method minimizes the dropping or blocking of emergency calls even if the number of emergency calls are more than 25% of the calls. Monte Carlo simulation results show that the proposed scheme works better than the existing adaptive probabilistic scheduling scheme (APS).

**Verdict:** FLAG: BORDERLINE (more of an EE paper applied to sleep but passable)

---

##   3. [W2153623436](https://openalex.org/W2153623436) — 2003 — article — `uniform`

**Concepts:** Flicker noise (0.77), Biasing (0.75), Phase noise (0.74), dBc (0.54), Offset (computer science) (0.43)

**Title:** Tail current flicker noise reduction in LC VCOs by complementary switched biasing

> A new LC voltage-controlled oscillator circuit topology is proposed, in which the flicker noise generated by the tail transistor is noticeably reduced by utilizing the phenomenon of flicker noise intrinsic reduction due to switched biasing. A macro model of MOSFET under switched biasing is used to prove the idea. Circuit simulations are done on two oscillators with the same tail current value; one with fixed biasing and the other with the proposed switching. A 4 dBc/Hz phase noise improvement is achieved at 1 kHz frequency offset in the switched biasing scheme under the same power dissipation and tuning range.

**Verdict:** FLAG: BORDERLINE (more of an EE paper applied to sleep but passable)

---

##   4. [W2347167563](https://openalex.org/W2347167563) — 2015 — article — `uniform`

**Concepts:** Prompt neutron (0.66), Physics (0.61), Neutron (0.61), Delayed neutron (0.60), Nuclear physics (0.58)

**Title:** Delayed neutron fraction and prompt decay constant measurement in the Minerve reactor using the PSI instrumentation

> The critical decay constant (β/Λ), delayed neutron fraction (β) and generation time (Λ) of the Minerve reactor were measured by the Paul Scherrer Institut (PSI) and the Commissariat à l'Energie Atomique (CEA) in September 2014 using the Feynman-α and Power Spectral Density neutron noise measurement techniques. Three slightly subcritical configuration were measured using two 1-g 235U fission chambers. This paper reports on the results obtained by PSI in the near critical configuration (-2⊄). The most reliable and precise results were obtained with the Cross-Power Spectral Density technique: β = 708.4±9.2 pcm, β/Λ = 79.0±0.6 s-1 and Λ = 89.7±1.4 μs. Predictions of the same kinetic parameters were obtained with MCNP5-v1.6 and the JEFF-3.1 and ENDF/B-VII.1 nuclear data libraries. On average the predictions for β and β/Λ overestimate the experimental results by 5% and 11%, respectively. The discrepancy is suspected to come from either a corruption of the data or from the inadequacy of the point kinetic equations to interpret the measurements in the Minerve driven system.

**Verdict:** OK

---

##   5. [W2605326475](https://openalex.org/W2605326475) — 2017 — article — `uniform`

**Concepts:** Computer science (0.89), Network packet (0.75), Computer network (0.70), Routing (electronic design automation) (0.64), Scheme (mathematics) (0.59)

**Title:** Efficient Producer Mobility Support in Named Data Networking

> Named Data Networking (NDN) is a promising architecture for the future Internet and it is mainly designed for efficient content delivery and retrieval. However, producer mobility support is one of the challenging problems of NDN. This paper proposes a scheme which aims to optimize the tunneling-based producer mobility solution in NDN. It does not require NDN routers to change their routing tables (Forwarding Information Base) after a producer moves. Instead, the Interest packet can be sent from a consumer to the moved producer using the tunnel. The piggybacked Data packet which is sent back to the consumer will trigger the consumer to send the following Interest packets through the optimized path to the producer. Moreover, a naming scheme is proposed so that the NDN caching function can be fully utilized. An analysis is carried out to evaluate the performance of the proposal. The results indicate that the proposed scheme reduces the network cost compared to related works and supports route optimization for enhanced producer mobility support in NDN.

**Verdict:** OK

---

##   6. [W2951693171](https://openalex.org/W2951693171) — 2014 — preprint — `uniform`

**Concepts:** Pairing (0.87), Condensed matter physics (0.80), Fermi surface (0.77), Physics (0.74), Cuprate (0.71)

**Title:** "Nodal gap" induced by the incommensurate diagonal spin density modulation in underdoped high-$T_c$ superconductors

> Recently it was revealed that the whole Fermi surface is fully gapped for several families of underdoped cuprates. The existence of the finite energy gap along the $d$-wave nodal lines ("nodal gap") contrasts the common understanding of the $d$-wave pairing symmetry, which challenges the present theories for the high-$T_c$ superconductors. Here we propose that the incommensurate diagonal spin-density-wave order can account for the above experimental observation. The Fermi surface and the local density of states are also studied. Our results are in good agreement with many important experiments in high-$T_c$ superconductors.

**Verdict:** OK

---

##   7. [W4402624116](https://openalex.org/W4402624116) — 2024 — article — `uniform`

**Concepts:** Computer science (0.74), Adaptive neuro fuzzy inference system (0.56), Malware (0.56), Android malware (0.41), Artificial intelligence (0.33)

**Title:** ANFIS-AMAL: Android Malware Threat Assessment Using Ensemble of ANFIS and GWO

> Abstract The Android malware has various features and capabilities. Various malware has distinctive characteristics. Ransomware threatens financial loss and system lockdown. This paper proposes a threat-assessing approach using the Grey Wolf Optimizer (GWO) to train and tune the Adaptive Neuro-Fuzzy Inference System (ANFIS) to categorize Android malware accurately. GWO improves efficiency and efficacy in ANFIS training and learning for Android malware feature selection and classification. Our approach categorizes Android malware as a high, moderate, or low hazard. The proposed approach qualitatively assesses risk based on critical features and threats. Our threat-assessing mechanism’s scale categorizes Android malware. The proposed approach resolves the issue of overlapping features in different types of malware. Comparative results with other classifiers show that the ensemble of GWO is effective in the training and learning process of ANFIS and thus achieves 95% F-score, 94% specificity, and 94% accuracy. The ensemble makes fast learning possible and improves classification accuracy.

**Verdict:** OK

---

##   8. [W4380360325](https://openalex.org/W4380360325) — 2023 — article — `uniform`

**Concepts:** Hadronization (0.77), Hadron (0.76), Multiplicity (mathematics) (0.66), Physics (0.65), Particle physics (0.56)

**Title:** Multiplicity of <mml:math xmlns:mml="http://www.w3.org/1998/Math/MathML" display="inline"><mml:mrow><mml:msub><mml:mrow><mml:mi>Z</mml:mi></mml:mrow><mml:mrow><mml:mi>c</mml:mi><mml:mi>s</mml:mi></mml:mrow></mml:msub><mml:mo stretchy="false">(</mml:mo><mml:mn>3985</mml:mn><mml:mo stretchy="false">)</mml:mo></mml:mrow></mml:math> in heavy ion collisions

> Using the coalescence model we compute the multiplicity of ${Z}_{cs}(3985{)}^{\ensuremath{-}}$ (treated as a compact tetraquark) at the end of the quark gluon plasma phase in heavy ion collisions. Then we study the time evolution of this state in the hot hadron gas phase. We calculate the thermal cross sections for the collisions of the ${Z}_{cs}(3985{)}^{\ensuremath{-}}$ with light mesons using effective Lagrangians and form factors derived from QCD sum rules for the vertices ${Z}_{cs}{\overline{D}}_{s}^{*}D$ and ${Z}_{cs}{\overline{D}}_{s}{D}^{*}$. We solve the kinetic equation and find how the ${Z}_{cs}(3985{)}^{\ensuremath{-}}$ multiplicity is affected by the considered reactions during the expansion of the hadronic matter. A comparison with the statistical hadronization model predictions is presented. Our results show that the tetraquark yield increases by a factor of about 2--3 from the hadronization to the kinetic freeze-out. We also make predictions for the dependence of the ${Z}_{cs}(3985{)}^{\ensuremath{-}}$ yield on the centrality, the center-of-mass energy and the charged hadron multiplicity measured at midrapidity $[d{N}_{ch}/d\ensuremath{\eta}(\ensuremath{\eta}&lt;0.5)]$.

**Verdict:** OK

---

##   9. [W2030174386](https://openalex.org/W2030174386) — 1984 — article — `uniform`

**Concepts:** Computer science (0.78), Access method (0.56), Index (typography) (0.52), Public access (0.51), Primary (astronomy) (0.50)

**Title:** KSAM

> This paper reports research undertaken to design and implement a B+-tree-based keyed sequential-access method (KSAM). KSAM provides primary and secondary access, which can be based on direct or sequential processing. Primary access to a data file requires three levels of indexes: super, master, and primary indexes. Secondary access requires an additional index level: secondary indexes. The superindex and master indexes are transparent to the user and are used solely by the system.

**Verdict:** OK

---

##  10. [W7132538725](https://openalex.org/W7132538725) — 2025 — dissertation — `uniform`

**Concepts:** Physics (0.62), Humanities (0.42), Theology (0.34), Engineering (0.33), Computer science (0.31)

**Title:** Urban Waterfront Revitalization of Grčevo, Integrating 3D Technologies and Sustainable Solutions

> Obale gradova definirane su kao prijelazne zone između urbanog tkiva i vode. One se često smatraju pokretačima urbanog razvoja jer njihovo uređenje ima potencijal stvoriti novu sliku grada, privući investicije i spriječiti propadanje prostora. Ovaj rad predlaže cjelovito uređenje obale na području Grčeva, na potezu od brodogradilišta Viktor Lenac do lučice Borik. Projekt obuhvaća izgradnju suvremene obalne šetnice, uređenje plažnih prostora i formiranje žala, kao i stvaranje uvjeta za smještaj suhe marine (suhe komunalne luke) namijenjene plovilima, čime se prostor obogaćuje dodatnim sadržajima javne i rekreativne namjene. Cilj je revitalizirati sada zapušten i infrastrukturno nedovoljno razvijen dio obale, stvarajući pritom funkcionalan, siguran i krajobrazno privlačan javni prostor. Primarni naglasak stavljen je na projektiranje šetnice, dok su za ostale objekte dane okvirne dimenzije, preliminarna situacija i lokacija izgradnje. Metodološki okvir rada temelji se na primjeni suvremenih tehnologija snimanja i digitalne dokumentacije prostora. Korištenjem LiDAR-a, ručnog LiDAR-a te 3D oblaka točaka, uz primjenu SLAM HLS tehnologije, provodi se precizno trodimenzionalno mapiranje obalnog pojasa. Tako prikupljeni podaci omogućuju detaljnu analizu topografskih, infrastrukturnih i prirodnih elemenata te služe kao podloga za planiranje optimalnih rješenja.

**Verdict:** FLAG: WRONG_FIELD (most likely wrong field)

---

##  11. [W7128767361](https://openalex.org/W7128767361) — 2026 — article — `uniform`

**Concepts:** Chemometrics (0.82), Process analytical technology (0.62), Manufacturing engineering (0.54), Process engineering (0.54), Process (computing) (0.53)

**Title:** Supporting Process Analytical Technology in Pharmaceutical Manufacturing With Lean Chemometrics

> The calibration burden of developing chemometric techniques to extract relevant information from spectral data is a barrier to spectroscopic process analytical technology (PAT) adoption in the pharmaceutical industry.Calibration burden refers to the time, material, and financial cost involved with generating representative calibration samples and corresponding reference data.The primary driver of calibration burden in precommercial pharmaceutical PAT applications is the high expense and limited availability of active pharmaceutical ingredients, particularly during early drug development stages.The concept of lean chemometrics is introduced to reduce calibration burden by leveraging multivariate data analysis methods that incorporate time-saving, material-sparing, and cost-cutting strategies.This article provides a definition and scope of lean chemometrics alongside a discussion on how to integrate these techniques with spectroscopic PAT to enable fit-for-purpose applications in pharmaceutical manufacturing.There are many chemometric techniques that meet the definition of lean chemometrics and have been demonstrated within the scientific literature to reduce calibration burden for spectroscopic PAT deployment.By formalizing lean chemometrics, the authors hope to raise awareness of historic methods and encourage the development of new lean chemometric techniques to overcome the notable challenge of the calibration burden.This is done with the goal of easing and expanding spectroscopic PAT adoption in the pharmaceutical industry and related sectors.

**Verdict:** FLAG: WRONG_FIELD

---

##  12. [W2468653858](https://openalex.org/W2468653858) — 1992 — article — `uniform`

**Concepts:** Markov random field (0.76), Artificial intelligence (0.71), Segmentation (0.67), Computer science (0.57), Computer vision (0.53)

**Title:** Markov random field contextual models in computer vision

> Many low-level vision processes need to incorporate contextual information to counteract the effects of sensor noise and incomplete knowledge about the sensing process and the scene. Context represents a priori assumptions about the physical world such as continuity and smoothness. This research explores the use of Markov random field (MRF) models to specify the contextual information in low-level vision processes. Two important low-level processes considered here are: edge detection in range images and fusion of intensity and range images.
We propose an MRF model-based algorithm to detect edges in range images. The edge-based segmentation is integrated with a region-based segmentation scheme resulting in a hybrid algorithm for surface segmentation. Results of edge detection and segmentation experiments presented on several real range images demonstrate the superior performance of the MRF model-based approach.
The MRF prior model used in our edge detection algorithm needs the specification of several parameters. The main difficulty in estimation of these parameters is that sufficient ground truth information is not easily available. We develop a new scheme for the estimation of MRF line process parameters which uses geometric CAD models of the 3D objects expected to be present in the scene. A canonical representation of clique potentials is used to reduce the number of model parameters. This parameter estimation scheme is further extended to estimate the parameters of the MRF prior model for the problem of edge detection in intensity images. Edge detection results using real range and intensity images indicate that performance with estimated parameters is as good as with the best parameters selected using trial and error procedure.
The thesis also explores the use of MRF models to capture contextual information in the problem of detection and labeling of edges by fusing information from registered intensity and range images. The key idea in this approach is that fusion of information from range and intensity images can be carried out by using a single physically meaningful edge label for each edge location. Experimental results on several real range-intensity image pairs are presented. The issue of computational requirements of the algorithm is also discussed, and the computational performance of two parallel computer implementations of the algorithm on a Connection Machine CM-2 are studied.
The results of edge detection and fusion experiments demonstrate the effectiveness of Markov random fields as models of contextual information for low-level vision problems.

**Verdict:** OK

---

##  13. [W4404619172](https://openalex.org/W4404619172) — 2024 — article — `uniform`

**Concepts:** Gynecology (0.52), Physics (0.44), Philosophy (0.33), Medicine (0.25)

**Title:** ÇİN-JAPONYA İLİŞKİLERİNDE ULUSLARARASI SİSTEM KAYNAKLI DEĞİŞİMLER: TEHDİT DENGESİ TEORİSİ BAĞLAMINDA BİR DEĞERLENDİRME

> Bu çalışma, on dokuzuncu yüzyılın sonlarında belirgin şekilde uluslararası sisteme eklemlenen Japonya ve Çin’in, bu tarihlerden günümüze kadar olan dönemdeki ikili ilişkilerini ve bu ilişkilerin uluslararası sistemin etkisiyle uğradığı değişimleri “Tehdit Dengesi Teorisi” bağlamında açıklamayı amaçlamaktadır. Çalışmada Japonya ve Çin ilişkilerinin tarihi, sistem düzeyinde ve sistem dönemlerine göre değerlendirilmiştir. İki ülkenin on dokuzuncu yüzyılın sonlarından günümüze kadar sırasıyla çok kutuplu, çift kutuplu ve son olarak tek kutuplu veya gevşek tek kutuplu sistemlerdeki ilişkilerinin değişimleri anlatılmış ve bu şekilde dönemsel olarak ortaya çıkan farklılıklar açıklanmaya çalışılmıştır. İki ülke arasında ortaya çıkan bu farklılıkların sebebi realist teori kapsamında Stephen Walt’un öne sürdüğü Tehdit Dengesi Teorisi ile tespit edilmeye çalışılmıştır. Çalışmada, tehdit algılarının değişiminin değerlendirilmesi ve tespiti de Tehdit Dengesi Teorisi kapsamında öne sürülen dört değerlendirme birimine göre yapılmıştır. Bu bağlamda çalışmada ilk olarak, Tehdit Dengesi Teorisi ve değerlendirme birimleri açıklanmıştır. Ardından, günümüze değin Çin-Japonya ilişkileri gözden geçirilmiş ve iki ülke arasındaki temel sorunlar açıklanmıştır. Son olarak, on dokuzuncu yüzyılın sonlarından günümüze kadar geçen sürede meydana gelen sistem değişikliklerinin iki ülke ilişkileri üzerine yansımaları dört değerlendirme birimi temelinde ve tehdit algısı bağlamında değerlendirilmiştir. Varılan sonuca göre, geleneksel rakipler olarak kendileri için birbirlerinden daha büyük tehlikeler hissettikleri dönemlerde Çin ve Japonya daha iyi ilişkilere sahip olmuşlardır. Uluslararası sistemin yapısında kaynaklı olarak kendilerine yönelmiş daha büyük tehditler görmediklerinde ise iki ülke daha sorunlu ve çatışmacı dönemler geçirme başlamışlardır.

**Verdict:** FLAG: WRONG_FIELD

---

##  14. [W3025751575](https://openalex.org/W3025751575) — 1997 — dissertation — `uniform`

**Concepts:** Computer science (0.72), Speech recognition (0.66), Multiplexer (0.60), Frame (networking) (0.54), Speech coding (0.52)

**Title:** An intelligent multiplexer architecture for thin route communications

> The main aim of the work reported in this thesis was to investigate and develop ways of increasing the throughput of a multiplexer for voice calls by introducing some intelligence into it so that the voice frames with least subjective significance are discarded. The discarded frames of the corresponding users are faithfully reconstructed at the receiver. The proposed intelligent multiplexer simulations are based on total five frame discarding techniques; three criterion and two non criterion based techniques. It is concluded that frame discarding techniques and Lost Frame Reconstruction (LFR) have a great potential of bandwidth savings. Generally criterion based frame discarding techniques perform better than none criterion based schemes. Digital Speech Interpolation (DSI) advantage) is achieved for monologue speech at 3% frame discarding rate, i.e., 1.33. For dialogue speech a DSI advantage of 2.0, can be achieved at 3% frame loss rate as indicated by analysis. The bandwidth efficiency can be increased by designing LFR schemes that can cater for changing characteristics of the speech signal, such as transitional regions of speech. The additional increase can also be achieved by investigating frame discarding techniques based on the perceptual importance of the speech signal. This thesis consists of 7 chapters. In the first 2 chapters the introduction of thesis and the background of Speech Interpolation (SI), systems employing Time Assignment Speech Interpolation (TASI), Digital Speech Interpolation (DSI) and LFR techniques are described. In the third chapter, the low bit rate speech coding is covered. In chapter 4 statistical measures of speech temporal parameters, such as talkspurts and silences are presented. These measures are then used for the simulation of talkspurts and silences by 2-state Markov model to represent speech sources. Also the tools and techniques developed for simulation are presented in chapter 4. The chapters 5-7 of the thesis consists of simulation results and suggestions for further work.

**Verdict:** FLAG: BORDERLINE (likely ok but link is broken so cannot verify)

---

##  15. [W4287777920](https://openalex.org/W4287777920) — 2020 — article — `uniform`

**Concepts:** Computer science (0.50)

**Title:** КРИТИЧНІ АСПЕКТИ ПОБУДОВИ ЕКСТЕРНАЛЬНОЇ СИСТЕМИ КОРПОРАТИВНОГО УПРАВЛІННЯ В УКРАЇНІ: ТЕОРЕТИЧНІ ПОЛОЖЕННЯ

> Корпоративне управління є формою організації діяльності корпорації через впорядкований вплив суб’єктів такого управління, їх взаємодію на мікроекономічні процеси, які забезпечують її оптимальне соціоекономічне існування в макроекономічному середовище. Оптимальність соціального і економічного існування відображає рівень досягнення поставлених цілей, мети діяльності корпорації. Не зважаючи не єдність в розумінні значення корпоративного управління, на сьогодні спостерігається чітка диференціація підходів до формування системи управління корпорацією, складу відповідних органів. Очевидним той факт, що в їх основі соціокультурна та економічна специфічність відповідного регіону, що обумовлює індивідуалізацію розвитку макроекономічних ринків.Класичним на сьогоднішньому етапі розвитку суспільства є система екстернального управління (США, Великобританія) передбачає вплив, на розвиток корпорації, отже на модель управління нею, екзогенних економічних факторів, таких, наприклад, як макроекономічні ринки. Індикатором ефективності корпоративного управління виступає рівень капіталізації корпорації на фондовому ринку. В наведеному випадку, акціонерний капітал має низький рівень своєї концентрації з високим рівнем залежності його оборотоздатності від фондового індексу, поточного котирування відповідного фінансового активу. Ефективність корпоративного управління призводить до зміни позитивної динаміки котирування відповідного фінансового активу і навпаки, слабе управління має наслідком зниження вартості активу. Отже фондовий ринок, як основне джерело фінансування, є об’єктивним і саморегулюючим фактором встановлення ефективності корпоративного управління. Висока залежність рівня капіталізації корпорації від зовнішніх факторів, зокрема макроекономічних індикаторів, є свідченням переважаючого характеру спекулятивності руху акціонерного капіталу, отже короткострокові інтереси інвесторів. Наведені умови впливають на формування моделі корпоративного управління.Цей підхід є доволі спрощений та несистемний, а також позбавлений відповідних правових гарантій доброчесності всіх учасників відносин. Безспірно, що в наведений спосіб значно спрощується механізм передачі важелів корпоративного управління юридичною особою. Але, в той же час, відбувається підміна відповідних юридичних категорій.Автором аргументовано, що збереження цілісності полірівневої системи управління корпорацією (скоординоване управління на рівні вищого органу, з управлінням на рівні виконавчого органу корпорації) завдяки можливої трансформації виключно консолідованого комплексу відповідних прав зменшує ризики корпоративного конфлікту між ними, який є одним із тягарів результативності в діяльності корпорації.

**Verdict:** FLAG: WRONG_FIELD

---

##  16. [W2291718387](https://openalex.org/W2291718387) — 2015 — article — `uniform`

**Concepts:** Computer vision (0.87), Artificial intelligence (0.85), Computer science (0.76), Mobile robot (0.73), Segmentation (0.70)

**Title:** A fast object segmentation method for mobile robots based on improved depth information

> Due to the rapid development of mobile robots technology, the object recognition is of great practical significance. The real-time performance and robustness of object segmentation in cluttered environments is a considerable problem in robot vision. In this paper, a new object segmentation method using depth information is presented. Firstly, this approach obtains the object candidate region using the depth clue, then accomplished the depth filtering in the object candidate region. Next, the object region is extended to get the better edge information. Finally, the foreground is extracted and the segmentation results is realized on the color image. This method of object segmentation was tested on a real mobile robot platform and the results of experiments confirmed the excellent performance of the proposed method.

**Verdict:** _____

---

##  17. [W2153116986](https://openalex.org/W2153116986) — 1999 — article — `uniform`

**Concepts:** Computer science (0.76), Computer vision (0.63), Artificial intelligence (0.63), Image registration (0.51), Segmentation (0.49)

**Title:** A minimax entropy registration framework for patient setup verification in radiotherapy

> In external beam radiotherapy (EBRT), patient setup verification over the entire course of fractionated treatment is necessary for accurate delivery of a specified dose to the tumor. We are working on the development of a minimax entropy registration framework for patient setup verification using dual portal images and the treatment planning 3D CT dataset. In this paper, we present an overview of our registration framework, where an iteratively and automatically estimated segmentation of the portal image is utilized to more accurately and robustly register the portal image to the 3D treatment-planning CT data. In addition, we describe initial testing of this approach. We note that, due to low resolution and low contrast of the portal images, this registration presents a difficult problem. We also note that the registration of the images in our proposed method is guided by the bony structure visible in the portal and the 3D CT images. However, since the prostate can move with respect to the pelvic bone, we propose using ultrasound images to quantify this movement.

**Verdict:** _____

---

##  18. [W2951302004](https://openalex.org/W2951302004) — 2019 — article — `uniform`

**Concepts:** Process (computing) (0.64), Context (archaeology) (0.62), Computer science (0.59), Driving simulator (0.53), Point (geometry) (0.44)

**Title:** A Game-Based Driving Learning System for Sri Lankan Driving Learners to Enrich the Awareness of Road Rules

> Traffic safety is becoming an important problem in most of the countries. Based on investigations it has been identified that the unawareness of road rules, lack of practice of sudden reactions in hazardous situations are the major causes for accidents. Though there are many driving simulators available, most of them have not addressed the road rules and hazardous incidences that a driver must be aware. Also they are lacking of a proper evaluation of the driving skills and awareness of the driver. Primary objective of the system is to provide a driving learning platform for the learners, trainers as well as evaluators to overcome the existing challenges, which has mainly focused on creating a virtual environment to facilitate the training and testing process in the local context and main areas of violating road rules and regulations by drivers are taken into account. In order to provide a realistic road environment, virtual environments are modeled based on different criteria. Artificial Intelligence techniques like non-player characters and objects, are employed. One of the major components of the simulator is the driver evaluation: a point based method defined upon the rules, road conditions and driving ethics established in the country. Further, the virtual environment provides all the road conditions available, countryside as well as the urban traffic conditions with different weather conditions. The effectiveness of the developed simulator is measured by allowing a selected group of learners to use the simulator for a specific period and assess their driving skills. It can be concluded that training the learners in a virtual environment that similar to the real environment with a proper assessment of their driving skills, awareness of the rules and road signs, and the driving ethics will solve most of the problems we face today.

**Verdict:** _____

---

##  19. [W3020420238](https://openalex.org/W3020420238) — 2017 — article — `uniform`

**Concepts:** AUTOSAR (0.88), Computer science (0.57), Embedded system (0.41), Real-time computing (0.34), Operating system (0.30)

**Title:** Automated configuration of time-critical multi-configuration AUTOSAR systems

> The vision of automated driving demands a highly available system, especially in safety-critical functionalities. In automated driving when a driver is not binding to be a part of the control loop, the system needs to be operational even after failure of a critical component until driver regain the control of vehicle. In pursuit of such a fail-operational behavior, the developed design process with software redundancy in contrast to conventional dedicated backup requires the support of automatic configurator for scheduling relevant parameters to ensure real-time behavior of the system. Multiple implementation methods are introduced to provide an automatic service which also considers task criticality before assigning task to the processor. Also, a generic method is developed to generate adaptation plans automatically for an already monitoring and reconfiguration service to handle fault occurring environment.

**Verdict:** _____

---

##  20. [W3096684918](https://openalex.org/W3096684918) — 2020 — article — `uniform`

**Concepts:** Filter (signal processing) (0.60), Computer science (0.60), Algorithm (0.58), Filter design (0.57), Minification (0.54)

**Title:** Low Complexity FIR Filter Design using Biogeography Optimization Algorithm and its Improved Version

> In this paper, sparse FIR filter design using multiobjective bio geography based optimization is considered. The metaheuristic bio geography based optimization algorithm is inspired by geographical science. It is easier in implementation, robust and faster in convergence. The objective function of filter design includes minimization of pass band ripples and stop band ripples. The tradeoff between the pass band ripple and stop band ripple cannot be solved by a single objective function and therefore a multiobjective optimization problem is formulated to solve the filter design problem. The evaluation of the proposed method is divided into two parts. In the first part, sparse FIR filter designed with the desired filter specification. In the second part, designed sparse FIR filter compared with the existing reporting algorithms. The comparison result shows the proposed method performs better than the existing algorithm and can be used in practical application.

**Verdict:** _____

---

##  21. [W2743660919](https://openalex.org/W2743660919) — 2006 — article — `uniform`

**Concepts:** Confocal (0.77), Image (mathematics) (0.66), Computer vision (0.65), Artificial intelligence (0.61), Image processing (0.59)

**Title:** 738 Development of Cell Function Analysis Technology Employing Three-Dimensional Image Processing Technology

> This research concerns developing the technique for analyzing various functions in the cell by making three-dimensional image maps from the successive section images of the fluorescently-stained cell that are acquired with a confocal laser scanning microscope (LSM). The distribution of fluorescence in the cell that is incomprehensible in two-dimensional image analysis can be investigated by three-dimensional image analysis. In the successive section images acquired with LSM, there are a lot of noises that disturb the construction of the three-dimensional image. Removing them without loss of the original information is an important problem to be solved. And, we succeeded in the development of the effective image processing method to achieve this and the method of the display that facilitates the observation of the fluorescent distribution. We removed the noises in the images of the stained nucleus and antibody cell, and then we actually analyzed it by making the three-dimensional images.

**Verdict:** _____

---

##  22. [W4200020443](https://openalex.org/W4200020443) — 2021 — article — `uniform`

**Concepts:** Discriminator (0.72), Computer science (0.52), Cloud computing (0.52), Pixel (0.48), Generator (circuit theory) (0.46)

**Title:** Algorithm Development of Cloud Removal from Solar Images Based on Pix2Pix Network

> Sky clouds affect solar observations significantly. Their shadows obscure the details of solar features in observed images. Cloud-covered solar images are difficult to be used for further research without pre-processing. In this paper, the solar image cloud removing problem is converted to an image-to-image translation problem, with a used algorithm of the Pixel to Pixel Network (Pix2Pix), which generates a cloudless solar image without relying on the physical scattering model. Pix2Pix is consists of a generator and a discriminator. The generator is a well-designed U-Net. The discriminator uses PatchGAN structure to improve the details of the generated solar image, which guides the generator to create a pseudo realistic solar image. The image generation model and the training process are optimized, and the generator is jointly trained with the discriminator. So the generation model which can stably generate cloudless solar image is obtained. Extensive experiment results on Huairou Solar Observing Station, National Astronomical Observatories, and Chinese Academy of Sciences (HSOS, NAOC and CAS) datasets show that Pix2Pix is superior to the traditional methods based on physical prior knowledge in peak signal-to-noise ratio, structural similarity, perceptual index, and subjective visual effect. The result of the PSNR, SSIM and PI are 27.2121 dB, 0.8601 and 3.3341.

**Verdict:** _____

---

##  23. [W7141945970](https://openalex.org/W7141945970) — 2026 — preprint — `uniform`

**Concepts:** Physics (0.61), Electromagnetic shielding (0.46), Multiplet (0.45), Nonlinear system (0.41), Dark energy (0.38)

**Title:** Chronowaves as a New Communication Channel

> Abstract This paper provides a theoretical and engineering framework for a novel communication channel based on the temporal multiplet (field φ) within the Temporal Theory of the Universe (TTU). Addressing the fundamental limits of the electromagnetic paradigm — spectral congestion and EMI shielding — we propose a transition to Layer 0: the spacetime substrate. The information carrier is defined as a scalar chronowave, a longitudinal perturbation of time density. We analyze the pre-cursor effect, where substrate phase-state shifts precede the inertial response of matter, creating an informational lead time. The proposed architecture utilizes geometric signal amplification (Kozyrev focus) and a multi-tier detection stack (quantum, mechanical, and resonant). We formalize the "Dark Channel" protocol (CW-PSK, Kiev Correlation Protocol), ensuring signal permeability through plasma and metallic barriers. Historical anomalies (EM Drive, superconductivity) are unified under a predicted 0.45 MHz universal resonance, transitioning astronomical observation from passive retrospection to an operational present. Keywords: Chronowave, Layer 0, TTU/TTG, pre-cursor effect, 0.45 MHz resonance, scalar perturbation, disformal coupling, "Dark Channel", operational present. TABLE OF CONTENTS 1. Introduction: Crisis of the Energy Paradigm 1.1. Maxwell's Limits: "Spectral Hunger" and the Energy Dead End 1.2. The Shielding Problem: Where Light is Powerless 1.3. Paradigm Shift: From Photons to Substrate Structure 2. Physics of the Carrier: The Temporal Multiplet and the φ Field 2.1. The φᵃ Substrate: The Fundamental "Data Bus" of the Universe 2.2. Disformal Coupling: Logarithmic Potential and Nonlinearity 2.3. Chronowave as a Scalar: Longitudinal Perturbations vs. EM Waves 3. The Precursor Effect: Informational Lead Time (v ≈ c) 3.1. Event Separation: Phase vs. Inertia 3.2. Lead Time Calculation (Δt): The Accumulated Lag Formula 3.3. Causality Compliance: Why This Is Not FTL 4. Geometric Amplification: The Kozyrev Focus 4.1. The Mirror as a Lens for Time: Compressing the Structure 4.2. The Local Differential Principle: The "Knife" Cutting Through Time 4.3. Gain Coefficient (G_geo): Paraboloid Geometry 5. The Tiered Hardware Stack: Detection Methods 5.1. Quantum Detector (Casimir Effect): Vacuum Pressure 5.2. Macro-Mechanical Sensor (Torsion Balance): Temporal Wind 5.3. Resonant Transducer: Tungsten and Quartz 5.4. Differential Bridge (Wheatstone–Kozyrev) 6. Layer 0 Protocol: Encoding and Super-Permeability 6.1. Phase Modulation (CW-PSK): Digital Signal in Temporal Potential 6.2. Kiev Correlation Protocol: Clarity from Noise 6.3. Engineering the "Dark Channel": Through Plasma and Steel 7. Conclusion: A New Era of Temporal Monitoring 7.1. Summary: The Superiority of the "Dark Channel" 7.2. Falsifiability of the Theory: Experimental Trigger 7.3. Operational Present: From Observer to Actor Appendix A. Historical Context and Unification of Anomalous Phenomena Within the Temporal Theory of the Universe (TTU)

**Verdict:** _____

---

##  24. [W7098526485](https://openalex.org/W7098526485) — 2015 — article — `uniform`

**Concepts:** Intelligent control (0.58), Control engineering (0.55), Mechatronics (0.52), Fuzzy logic (0.51), Controller (irrigation) (0.50)

**Title:** INTELLIGENT CONTROLLER FOR MAGNETOSTRICTIVE MICROPOSITIONING DEVICE FOR ULTRA-PRECISION

> Generally, requirements such as high performance and small sizes for mechatronic systems, have led modern industry to design positioning systems with better characteristics of acceleration and positioning accuracy. The increasing demand for components with better metrological and finishing characteristics such as x-ray and infra-red lenses, has prompted the development of a number of types of micropositioning systems that are able to move machine elements in very small displacements with high levels of accuracy. In this work, it is proposed the use of a new type of actuator, which employs the properties of electromagnetic strain of certain metallic alloys (magnetostrictive actuators). Digital control systems that use control algorithms based on fuzzy logic (FL) and artificial neural networks (ANN) for micropositioning control are considered and their application proposed.

**Verdict:** _____

---

##  25. [W4382462104](https://openalex.org/W4382462104) — 2023 — article — `uniform`

**Concepts:** Smoothing (0.88), Computer science (0.65), Algorithm (0.64), Global Positioning System (0.59), Noise (video) (0.58)

**Title:** An Optimal Carrier-Phase Smoothing Code Algorithm for Low-Cost Single-Frequency Receivers

> Carrier-phase smoothing code (CPSC) is a code-smoothing technology that uses carrier-phase changes to reduce code noise in Global Navigation Satellite System (GNSS) appliances. Although CPSC performs well in reducing noise and is easy to implement, it is a trade-off between the reduction of noise and the increase of the variation of ionospheric errors. The width of the smoothing window needs to be large to reduce noise. However, a wider smoothing window increases the variation of ionospheric errors. To circumvent this dilemma, the grid ionospheric model (GIM) was used to estimate the variation of ionospheric errors between consecutive epochs, and a noise estimation method is proposed for low-cost single-frequency receivers. Furthermore, an optimal carrier phase smoothing code (OCPSC) algorithm with an adaptive width smoothing window is proposed to reduce the noise of Global Positioning System (GPS) data. We found that the OCPSC is more robust and its positioning performance is better overall for low-cost single-frequency receivers than is the traditional CPSC. In a static mode, when applying the OCPSC algorithm, the positioning accuracy can be improved by 0.15 m (6%) and 0.06 m (6%) in the horizontal and vertical directions, respectively. These improvements are 0.08 (3%) m and 0.06 m (1%) when a kinematic mode is applied.

**Verdict:** _____

---

##  26. [W2588880359](https://openalex.org/W2588880359) — 2018 — article — `uniform`

**Concepts:** Theology (0.84), Physics (0.41), Philosophy (0.33)

**Title:** Analiza uwarunkowań społeczno-kulturowych wpływających na sytuację romskiego ucznia w polskim systemie edukacji

> W systemie wartości Romow wymiar edukacji zajmuje podrzedne miejsce. Dlatego Romowie pośrod innych grup etnicznych zamieszkujących Polske stanowią spolecznośc o najnizszym poziomie wyksztalcenia. Wśrod czlonkow tej grupy nadal klasyfikuje sie bardzo duzo analfabetow i osob z podstawowymi umiejetnościami pisania i czytania. Pomimo iz świadomośc edukacyjna, zwlaszcza mlodych pokolen, wzrasta, starsi Romowie do spraw nauki podchodzą  z dystansem i pewną dozą niecheci. Fakt niskiej frekwencji uczestnictwa Romow w edukacji czesto utozsamiany jest przez osoby nieznające specyfiki kultury romskiej, ich wrodzonym lenistwem i niską inteligencją. Argumenty te, w duzej mierze stereotypowe, w wielu przypadkach nie znajdują potwierdzenia w rzeczywistości. Istotne jest jednak to, iz pomimo tych krzywdzących i wielokrotnie nieprawdziwych ocen Romowie na ogol pozostają bierni i nie probują ich zmienic. Podobnie jest w kwestii inicjatywy tworzenia wlasnych instytucji edukacyjnych i kulturowych, do zakladania ktorych spolecznośc romska ma pelnie praw, jednocześnie ich nie wykorzystując. Romowie, bedąc obywatelami Polski, zobligowani są do przestrzegania obowiązującego w niej prawa, w tym czynnego uczestnictwa w procesie edukacyjnym. Jednak wielu Romow nie wypelnia obowiązku szkolnego, co ukazują chocby statystyki dotyczące liczby romskich absolwentow. Co jest wiec przyczyną niecheci Romow do nauki oraz jakie trudności napotyka romski uczen  w polskiej szkole? Na te i inne pytania odpowiadam w niniejszym artykule, ktorego celem jest ukazanie „barier” wynikających ze specyficznej kultury Romow, stojących na drodze do sukcesow edukacyjnych romskich uczniow.

**Verdict:** _____

---

##  27. [W2054013488](https://openalex.org/W2054013488) — 1997 — article — `uniform`

**Concepts:** Optics (0.78), Laser (0.70), Laser linewidth (0.68), Physics (0.67), Compton scattering (0.45)

**Title:** Compton backscattering focused x-ray source for advanced biomedical applications

> At ultrahigh intensities, where the normalized vector potential of the laser wave exceeds unity, the electron axial velocity modulation due to radiation pressure yields nonlinear Compton backscattered spectra. For applications requiring a narrow Doppler upshifted linewidth, such as the gamma-gamma collider or focused x-ray generation, this can pose a serious problem. It is shown that temporal laser pulse shaping using spectral filtering at the Fourier plane of a chirped pulse laser amplifier can alleviate this problem, and that this technique can be scaled to the required multi-TW range. Compton backscattered spectra are derived in three cases: hyperbolic secant, hybrid pulses (hyperbolic secant trnasient and flat-top), and square optical pulses similar to those experimentally obtained by Weiner et al. It is found that the optimum laser pulse shapes correspond to square pulses, yielding a high contrast ratio between the main spectral line and the transient lines. The corresponding spectral filter function is also determined, and its practical implementation in a chirped pulse laser amplifier is addressed.

**Verdict:** _____

---

##  28. [W4387113806](https://openalex.org/W4387113806) — 2023 — preprint — `uniform`

**Concepts:** Supply chain (0.81), Autoencoder (0.74), Computer science (0.65), Artificial intelligence (0.56), Deep learning (0.47)

**Title:** Disruption Detection for a Cognitive Digital Supply Chain Twin Using Hybrid Deep Learning

> Purpose: Recent disruptive events, such as COVID-19 and Russia-Ukraine conflict, had a significant impact of global supply chains. Digital supply chain twins have been proposed in order to provide decision makers with an effective and efficient tool to mitigate disruption impact. Methods: This paper introduces a hybrid deep learning approach for disruption detection within a cognitive digital supply chain twin framework to enhance supply chain resilience. The proposed disruption detection module utilises a deep autoencoder neural network combined with a one-class support vector machine algorithm. In addition, long-short term memory neural network models are developed to identify the disrupted echelon and predict time-to-recovery from the disruption effect. Results: The obtained information from the proposed approach will help decision-makers and supply chain practitioners make appropriate decisions aiming at minimizing negative impact of disruptive events based on real-time disruption detection data. The results demonstrate the trade-off between disruption detection model sensitivity, encountered delay in disruption detection, and false alarms. This approach has seldom been used in recent literature addressing this issue.

**Verdict:** _____

---

##  29. [W2039744893](https://openalex.org/W2039744893) — 2010 — article — `uniform`

**Concepts:** Jamming (0.85), Frequency-shift keying (0.81), Additive white Gaussian noise (0.80), Fading (0.66), Nakagami distribution (0.55)

**Title:** Performance analysis of FFH/MFSK receivers with noise‐normalisation combining over Nakagami‐<i>m</i>fading channels with partial‐band jamming

> Abstract The performance of a fast frequency‐hopped M ‐ary orthogonal frequency‐shift‐keying (FFH/MFSK) receiver with noise‐normalisation combining over Nakagami‐ m fading channels with partial‐band noise jamming and additive white Gaussian noise (AWGN) is analysed. Instead of numerical integration, a closed‐form error probability expression is obtained. The analytical results validate the simulation results. It is shown that there is an optimum diversity order and the corresponding best‐case performance is investigated. Copyright © 2010 John Wiley &amp; Sons, Ltd.

**Verdict:** _____

---

##  30. [W4365151782](https://openalex.org/W4365151782) — 2023 — article — `uniform`

**Concepts:** Metaverse (0.58), Computer science (0.44), World Wide Web (0.42), Virtual reality (0.20), Artificial intelligence (0.00)

**Title:** THE ENGINE IS THE MESSAGE: VIDEOGAME INFRASTRUCTURE AND THE FUTURE OF DIGITAL PLATFORMS

> On January 18, Microsoft revealed its $68.7 billion deal to acquire videogame publisher Activision Blizzard. The acquisition was pitched as an investment towards “metaverse platforms” that gaming would play a key role in developing. Journalists speculated about the increasing consolidation of the videogame industry and whether blockbuster franchises would be locked into Microsoft’s platforms and subscription services. Commentary on the metaverse weighed in on how toxicity and harassment in game industry workplaces such as Activision Blizzard might relate to issues of trust and safety in virtual worlds such as Meta’s Horizon Worlds. Seemingly above the fray of platform strategy, market speculation, and corporate scandal, New Yorker writer Kyle Chayka (2022) tweeted as a matter of fact: “video game infrastructure and tools are increasingly going to take over all digital platforms”. This panel contextualizes discussions about the business and aesthetics of 3D platforms in the infrastructural work of game engines, which routinely integrate databases, file formats, web protocols, and translational algorithms. We trace public debates and corporate statements over representation and governance, equity and inclusion (Bosworth 2021) to the techniques, technologies, and practices that enable massive real-time 3D digital spaces to flow and transact. We also highlight the growing intertwinement between game engine development companies and related content ecosystems, such as the Epic Games Store and the Unreal Engine, and Epic’s and Unity’s Asset Stores. This panel investigates how digital systems are designed to regulate technical interoperability and its implications for creative practice and cultural production. Together, these papers map how power and capital become centralized and distributed throughout the back end of the metaverse, and politicize how social practices and subjectivities are negotiated through technological architecture.

**Verdict:** _____

---

##  31. [W3138742400](https://openalex.org/W3138742400) — 2020 — book — `uniform`

**Concepts:** Computer science (0.44)

**Title:** Optimisation et analyse convexe

> L'auteur a fait sienne cette universelle maxime chinoise : « j'entends et j'oublie (cours oral) je vois et je retiens (étude du cours) je fais et je comprends » (exercices)… Ainsi, ce livre est un recueil d'exercices et problèmes corrigés, de difficulté graduée, accompagnés de commentaires sur l'utilisation du résultat obtenu, sur un prolongement possible et, occasionnellement, placés dans un contexte historique. Chaque chapitre débute par des rappels de définitions et résultats du Cours. Le cadre de travail est volontairement simple, l'auteur a voulu insister sur les idées et mécanismes de base davantage que sur des généralisations possibles ou des techniques particulières à telle ou telle situation. Les connaissances mathématiques requises pour tirer profit du recueil ont été maintenues minimales, celles normalement acquises à Bac+3 (ou Bac+2 suivant les cas). L'approche retenue pour avancer est celle d'une progression en spirale plutôt que linéaire au sens strict. Pour ce qui est de l'enseignement, les aspects de l'optimisation et analyse convexe traités dans cet ouvrage trouvent leur place dans les formations de niveau M1, parfois L3, (modules généralistes ou professionnalisés) et dans la formation mathématique des ingénieurs (en 2e année d'école, parfois en 1re année). La connaissance de ces aspects est un préalable à des formations plus en aval, en optimisation numérique par exemple. Détails: après un chapitre de révisions de base (analyse linéaire et bilinéaire, calcul différentiel), l'ouvrage aborde l'optimisation par les conditions d'optimalité (chap. 2 et 3), le rôle incontournable de la dualisation des problèmes (chap. 4) et le monde particulier de l'optimisation linéaire (chap.5). L'analyse convexe est traitée par l'initiation à la manipulation des concepts suivants : projection sur un convexe fermé (chap.6), le calcul sous différentiel et de transformées de Legendre-Fenchel (chap.7).

**Verdict:** _____

---

##  32. [W4414345173](https://openalex.org/W4414345173) — 2025 — article — `uniform`

**Concepts:** Quantum entanglement (0.85), Physics (0.72), Quantum mechanics (0.57), Statistical physics (0.54), Quantum (0.54)

**Title:** Quantum Information Perspective on Many-Body Dispersive Forces

> Despite its ubiquity, the quantum many-body properties of dispersion remain poorly understood. Here, we investigate the entanglement distribution in assemblies of quantum Drude oscillators, minimal models for dispersion-bound systems. We establish an analytic relationship between entanglement and correlation energy and show how entanglement monogamy determines whether many-body corrections to the pair potential are attractive, repulsive, or zero. These findings, demonstrated in trimers and extended lattices, apply in more general chemical environments where dispersion coexists with other cohesive forces.

**Verdict:** _____

---

##  33. [W7099199220](https://openalex.org/W7099199220) — 2009 — article — `uniform`

**Concepts:** Clutter (0.77), Point target (0.67), Algorithm (0.63), Track-before-detect (0.60), Robustness (evolution) (0.59)

**Title:** Particle Filter Based Algorithm for StateEstimation of Dim Moving Point Targets in

> Abstract—Under the condition of the targets ’ initial information is already estimated successfully, This paper presents a real-time target tracking method based on particle filter (PF) update algorithm. According to the particles &amp;apos; transmission characteristics and the measurements from a single frame detection, the algorithm estimate a target’s following moving state. In this way, the dim moving point target could be tracked successfully under the low signal-noise-ratio (SNR) in IR image sequence. But it comes to the multiple targets ’ tracking; we should take the data integration into account. In order to reduce the amount of calculation, we use the data fusion method to divide the measurements in the overlapped parts of windows, appoints the measurements for the corresponding target. That is the Nearest Neighbor Standard Filter (NNSF) theory is used to choose the target for a measurement. The paper introduced the related theory and the concrete steps for accomplish the algorithm and also simulated the proposed tracking algorithm on the MATLAB platform. Experimental analysis and results showed that the algorithm achieved real-time, dynamic stability and robustness while track the random moving targets in high clutter environment. Index Terms—particle filter, single frame detection, measurement division, state estimation, image sequence I.

**Verdict:** _____

---

##  34. [W2603876198](https://openalex.org/W2603876198) — 2016 — article — `uniform`

**Concepts:** Task (project management) (0.69), Object (grammar) (0.57), Physical medicine and rehabilitation (0.54), Computer science (0.47), Artificial intelligence (0.33)

**Title:** Credit Assignment across Limbs in a Bimanual Object Lifting Task (P4.063)

> Objective: To examine credit assignment during a natural object lifting task. Background: Despite our generally skilled interactions with the environment, the motor system invariably makes mistakes. For example, we may lift an object only to find that it is heavier than predicted. To learn from our mistakes, the cause of the error has to be identified by the motor system, a process termed credit assignment. The present study examined whether small errors in lifting forces generalized across limbs as a test of whether they are attributed to the self as opposed to the external environment. If the errors in lifting are attributed to the self, the accumulation of error should remain with the hand performing the lift. Methods: Twenty-nine students completed a bimanual object lifting task. The participant’s left hand always lifted the same block, whereas the right hand lifted a block that gradually increased in weight every ten trials. Following eighty lifts in which the weight in one hand gradually increased, the participant lifted a set of new blocks using a crossed-arm lifting style (lifting the block on the left with the right hand). The initial peak in load force rate (PkLFR) and the load force at the peak load force rate (LF@PkLFR), measures known to be sensitive to a participant’s weight prediction, were examined. Results: PkLFR and LF@PkLFR increased in the right hand between the first and last trial, indicating participants accommodated the change in object weight. However, during the crossed-arm object lifting trials, no differences between the hands were observed. Conclusions: This research suggests small errors in motor control are not always attributed to the self, and may at times be attributed to the external environment. By learning how error-based learning is accomplished, we can create better artificial limbs and more thoroughly assess motor impairments.

**Verdict:** _____

---

##  35. [W332268136](https://openalex.org/W332268136) — 1981 — article — `uniform`

**Concepts:** Photometry (optics) (0.73), Solar eclipse (0.66), Corona (planetary geology) (0.62), Brightness (0.61), Physics (0.55)

**Title:** Joint Soviet--French investigations of the solar corona. 2. Photometry of solar corona of June 30, 1973

> The results are presented on a study of eclipse negative obtained on June 30, 1973, in Africa in the program of the Soviet--French experiment ''Dynamics of the White Corona'' by expeditions of Kiev University (Atar, Mauritania) and the Paris Astropysical Institute (Moussoro, Chad). The distributions of the total brightness of the corona out to rapprox. =4.5 R/sub sun/ and of its K and F components for the E and N directions are found with high accuracy on the basis of a new method of photometry and colorimetry using the images of stars down to 8.5/sup m/ as photometric standards. Neither reddening nor flattening of the dusty F component were detected at r<2.5 R/sub sun/. The integral brightness of the corona in the standard zone (1.03--6.0 R/sub sun/) is 0.64 x 10/sup -6/ E/sub sun/.

**Verdict:** _____

---

##  36. [W2804252553](https://openalex.org/W2804252553) — 2018 — article — `uniform`

**Concepts:** Computer science (0.68), Reliability (semiconductor) (0.67), Demand response (0.61), Reliability engineering (0.55), Renewable energy (0.53)

**Title:** i13DR

> With the ongoing integration of Renewable Energy Sources (RES), the complexity of power grids is increasing. Due to the fluctuating nature of RES, ensuring the reliability of power grids can be challenging. One possible approach for addressing these challenges is Demand Response (DR) which is described as matching the demand for electrical energy according to the changes and the availability of supply. However, implementing a DR system to monitor and control a broad set of electrical appliances in real-time introduces several new complications including ensuring reliability and financial feasibility of the system. In this work, we address these issues by designing and implementing a distributed real-time DR infrastructure for laptops, which estimates and controls the power consumption of a network of connected laptops in response to the fast irregular changes of RES. The result of our field experiments confirms that our system successfully schedules and executes rapid and effective DR events. However, the accuracy of estimated power consumption of all participating laptops is relatively low, directly caused by our software-based approach.

**Verdict:** _____

---

##  37. [W7111010977](https://openalex.org/W7111010977) — 2025 — article — `uniform`

**Concepts:** Materials science (0.65), Photonics (0.60), Transistor (0.52), Optoelectronics (0.50), Broadband (0.49)

**Title:** Organic PhotonicSynapses with UV–Vis–NIRBroadband Perception Based on Organic Electrochemical Transistors

> Organic photonic synaptic devices have shown immense potential for emulating the visual perception function of the human retina. In particular, organic electrochemical transistors (OECTs) with photoresponse ability are considered promising choices because of their advantages in low-voltage operation, mechanical flexibility, and biocompatibility. However, current research is limited, and deeper investigations into the materials, devices, and their perception capability are needed. Herein, we introduce a solid-state organic electrochemical transistor based on an organic bulk heterojunction film, which exhibits a broadband response from ultraviolet to near-infrared (365–850 nm) and can simulate fundamental biological synaptic behaviors across multiple wavelengths. Moreover, the device can emulate the learning, forgetting, and relearning processes, as well as the image recognition and memory functions. By employing a trichromatic perception simulation based on convolutional operations, the device successfully achieves image preprocessing capabilities, demonstrating the promising potential of our OECT-based photonic synapses in artificial visual perception systems.

**Verdict:** _____

---

##  38. [W2378887358](https://openalex.org/W2378887358) — 2013 — article — `uniform`

**Concepts:** Generality (0.75), Test (biology) (0.65), Computer science (0.54), Process (computing) (0.50), Test data (0.45)

**Title:** The Generality and Analysis of Engine Performance Test

> This paper has generally discussed some problems during engine performance test and makes some summarizations about data analysis and equipment of engine performance test combined with actual situations.Summarized in this paper about how to complete the engine performance experiment effectively,and induced how to solve the test problems that you may encounter in the process of experiment.

**Verdict:** _____

---

##  39. [W7014994288](https://openalex.org/W7014994288) — 2000 — article — `uniform`

**Concepts:** Underwater acoustic communication (0.73), Underwater (0.70), Acoustics (0.58), Underwater acoustics (0.52), Computer science (0.51)

**Title:** The ROBLINKS underwater acoustic communication experiments:

> Within the EU-MAST III project ROBLINKS waveforms and algorithms have been developed to establish robust underwater acoustic communication links with high data rates Ã­n shallow water. To evaluate the signalling schemes a wide range of experiments has been performed during a sea trial that has been held in May 1999 in the North Sea, off rhe Dutch coast. The resulting data set consists of recordings of the newly developed waveforms, of more conventional communication signals for comparison, and of signals to probe the acoustic channel. Environmental data have also been collected to analyze and understand the propagation conditions during the transmissions. The most interesting and illustrative part of the data set will be made available for further analysis after the end of the ROBLINKS project

**Verdict:** _____

---

##  40. [W2077685954](https://openalex.org/W2077685954) — 1966 — article — `uniform`

**Concepts:** Bibliography (0.91), Computer science (0.55), Library science (0.37), Information retrieval (0.36), Political science (0.35)

**Title:** Soviet Centralized Bibliography

> After pointing to the critical need for comprehensive world bibliography both current and retrospective, the author describes the structure of Soviet bibliographic coverage. He gives reasons for certain aspects of Soviet bibliography which have on occasion in the past been criticized and describes some of the particular problems encountered in enumerating the productions of the Soviet press. He concludes with a statement concerning some of the weaknesses remaining in the Soviet system and describes prospects for their elimination.

**Verdict:** _____

---

##  41. [W2147043418](https://openalex.org/W2147043418) — 2014 — article — `uniform`

**Concepts:** Mach number (0.82), Aerodynamics (0.62), Cylinder (0.61), Reynolds number (0.61), Physics (0.59)

**Title:** Towards Simulation of Far-Field Aerodynamic Sound from a Circular Cylinder Using OpenFoam

> The low-Mach number flow-induced noise by the flow past a circular cylinder at sub-critical regime was predicted. First, to assess the accuracy of the numerical methodology, the laminar flow over a circular cylinder at the Reynolds number Re = 140 and Mach number M = 0.2 was calculated by direct solution of the unsteady compressible Navier-Stokes equations. Second, the sound generated by a circular cylinder at the Reynolds number Re = 2.2 × 10 4 and Mach number M = 0.06 was simulated using a technique of large-eddy simulation. For both cases, the calculated acoustic fields showed a dipole directivity, similar to a natural vortex shedding. The impact of the Doppler effect was investigated and discussed as well. In general, the computed aerodynamic and far-field acoustic results were found to be in good agreement with available experimental measurements and analytical relationships.

**Verdict:** _____

---

##  42. [W4411880848](https://openalex.org/W4411880848) — 2025 — book-chapter — `uniform`

**Concepts:** Overfitting (0.96), Regularization (linguistics) (0.70), Artificial intelligence (0.59), Computer science (0.50), Machine learning (0.42)

**Title:** Mitigating Overfitting and Underfitting in Deep Learning: A Comprehensive Study of Regularization Techniques

> The prominence of deep learning has been noted in a variety of fields owing to its capability of penetrating the complex layers of relationship that exists within data. However, one of the most vital factors in the training of deep learning models is the problem of overfitting and underfitting. A model is said to be overfitted when it controls noise rather than the model’s fundamental distribution and such models tend to perform indiscriminately poorly on unseen samples. Underfitting is the opposite and it is said to be the case when a model does not manage to learn the basic trend of the data and thus does not perform well. In this paper, the authors review the notion of regularization and how it helps to control overfitting and underfitting of deep learning models in different situations. The analysis incorporates several regularization techniques, such as L1 and L2 regularization, dropout, and data augmentation. The experimental results prove the efficiency of these techniques in improving the model performance of standard datasets. The results explain that there are some regularization techniques that are specific for certain model architectures and datasets.

**Verdict:** _____

---

##  43. [W2365176882](https://openalex.org/W2365176882) — 2012 — article — `uniform`

**Concepts:** Bridge (graph theory) (0.84), Wireless (0.59), Wireless network (0.56), Field (mathematics) (0.55), Wireless transmission (0.54)

**Title:** Application of wireless bridge to field water system

> It's important that real-time monitoring and the unified production management in the field scattered deep well pump house.Application of wireless bridge will realize systematic data live transmission,we can monitor the parameters'change which in the CCR may be clear at a glance,simultaneously we can check all pump house through the real-time video,the entire pump house realizes 24 hours unattended running;Application of wireless bridge in system is more easier to build and more cheaper then the traditional wired network,the network run cost approaches in zero,manpower and material resources can be reduced greatly.

**Verdict:** _____

---

##  44. [W2007040212](https://openalex.org/W2007040212) — 2010 — article — `uniform`

**Concepts:** Physics (0.58), Molecular biology (0.35), Biology (0.16)

**Title:** CITOLOGIA DE LAVADO BRONCOALVEOLAR DE CÃES: COMPARAÇÃO ENTRE LÂMINAS A FRESCO E CONSERVADAS EM FORMOL

> O lavado broncoalveolar em cães é um método diagnóstico recomendado em casos de enfermidades do trato respiratório inferior, quando exames de rotina não permitem um diagnóstico conclusivo. O exame baseia-se na análise citológica e confecção de lâminas com o material a fresco, ou seja, logo após a coleta, o que pode inviabilizar a técnica em casos de difícil acesso aos laboratórios especializados. Para isso, faz-se necessário um meio de conservação das amostras, aumentando o tempo de vida útil do material a ser analisado. Assim, realizou-se o lavado broncoalveolar em quatorze cães adultos saudáveis. As amostras foram separadas em duas alíquotas: a primeira confeccionada a fresco por sedimentação em câmara de Suta, e a segunda processada uma semana depois, com a amostra conservada em formol. As lâminas foram coradas pelo corante rápido Panótico. Avaliou-se o volume infundido e o volume recuperado, o aspecto macroscópico, a contagem de células nucleadas, a análise diferencial de células e a análise descritiva das lâminas quanto à celularidade, presença de muco, hemácias, leucócitos e células, íntegras ou degeneradas. A análise estatística foi realizada com teste t, para amostras pareadas com p&lt;0,05. Foram encontrados aumento significativo na quantidade de linfócitos e diminuição do número de macrófagos nas amostras conservadas em formol. As demais observações foram similares em ambos os grupos. Portanto, a conservação do material do lavado broncoalveolar de cão em formol, durante uma semana, preservou as células, tornando viável a técnica do lavado broncoalveolar.

**Verdict:** _____

---

##  45. [W3044815875](https://openalex.org/W3044815875) — 2020 — review — `uniform`

**Concepts:** Facial recognition system (0.75), Computer science (0.72), Three-dimensional face recognition (0.67), Identification (biology) (0.59), Artificial intelligence (0.59)

**Title:** Past, Present, and Future of Face Recognition: A Review

> Face recognition is one of the most active research fields of computer vision and pattern recognition, with many practical and commercial applications including identification, access control, forensics, and human-computer interactions. However, identifying a face in a crowd raises serious questions about individual freedoms and poses ethical issues. Significant methods, algorithms, approaches, and databases have been proposed over recent years to study constrained and unconstrained face recognition. 2D approaches reached some degree of maturity and reported very high rates of recognition. This performance is achieved in controlled environments where the acquisition parameters are controlled, such as lighting, angle of view, and distance between the camera–subject. However, if the ambient conditions (e.g., lighting) or the facial appearance (e.g., pose or facial expression) change, this performance will degrade dramatically. 3D approaches were proposed as an alternative solution to the problems mentioned above. The advantage of 3D data lies in its invariance to pose and lighting conditions, which has enhanced recognition systems efficiency. 3D data, however, is somewhat sensitive to changes in facial expressions. This review presents the history of face recognition technology, the current state-of-the-art methodologies, and future directions. We specifically concentrate on the most recent databases, 2D and 3D face recognition methods. Besides, we pay particular attention to deep learning approach as it presents the actuality in this field. Open issues are examined and potential directions for research in facial recognition are proposed in order to provide the reader with a point of reference for topics that deserve consideration.

**Verdict:** _____

---

##  46. [W2963807684](https://openalex.org/W2963807684) — 2019 — article — `uniform`

**Concepts:** Cosmic ray (0.89), Physics (0.84), Neutrino (0.80), Observatory (0.76), Neutrino detector (0.62)

**Title:** Cosmic ray composition study using machine learning at the IceCube Neutrino Observatory

> The evaluation of mass composition of cosmic rays in the knee region (~3 PeV) is critical to understanding the transition in the origin of cosmic rays from galactic to extragalactic sources. The IceCube Neutrino Observatory at the South Pole is a multi-component detector consisting of the surface IceTop array and the deep in-ice IceCube detector. By applying modern machine-learning techniques to cosmic-ray air showers reconstructed coincidentally in both detector components of IceCube observatory, the energy and the mass of primary cosmic rays in this transition region can be measured. In this contribution, we will discuss the reconstruction performance and composition sensitivity of IceCube observables presently under development.

**Verdict:** _____

---

##  47. [W1496376740](https://openalex.org/W1496376740) — 2012 — article — `uniform`

**Concepts:** Interfacing (0.90), Electromyography (0.71), Interface (matter) (0.71), Physical medicine and rehabilitation (0.60), Exoskeleton (0.56)

**Title:** Review of EMG-based neuromuscular modeling for the use of upper limb control

> Assistive robots have made great contributions to disabled people in physiotherapy and rehabilitation areas. The interface between patients and medical devices plays a significant role for patients to operate these kinds of robots. This review introduces the current research and development of neuromuscular interfaces, especially the new research directions with special focus on modeling of musculoskeletal systems for interfacing purposes. The paper also summarises the function and prominent advantage of using surface Electromyography (sEMG) signals for the interface. The elbow joint was used as an example to go through the working steps of both human biological systems and neuromuscular interfaces. Further developments were also discussed to improve the interface to meet medical demands.

**Verdict:** _____

---

##  48. [W7037981199](https://openalex.org/W7037981199) — 2000 — article — `uniform`

**Concepts:** Computer science (0.48), Quality (philosophy) (0.47), Artificial intelligence (0.46), Work (physics) (0.44), Odor (0.41)

**Title:** Fisher Information and Optimal Odor Sensors

> This is the author’s version of a work that was accepted for publication in Neurocomputing. Changes resulting from the publishing process, such as peer review, editing, corrections, structural formatting, and other quality control mechanisms may not be reflected in this document. Changes may have been made to this work since it was submitted for publication. A definitive version was subsequently published in Neurocomputing, vol,38-40 (2001) doi:10.1016/S0925-2312(01)00364-2

**Verdict:** _____

---

##  49. [W3035359449](https://openalex.org/W3035359449) — 2020 — article — `uniform`

**Concepts:** Computer science (0.69), Electroencephalography (0.63), Artificial intelligence (0.54), Dependency (UML) (0.50), Brain activity and meditation (0.49)

**Title:** Complex brain activity analysis and recognition based on multiagent methods

> Summary Brain activity recognition research has been a challenging area for many decades since Hans Berger described electroencephalogram (EEG) in 1929. Many previous researches cannot successfully identify EEG status due to dynamic brain activities and complicated brain correlation. This article adopts multiagent‐based methods to analyze EEG datasets, which can enhance the analytical efficiency through incorporating autonomous, self‐coordination characteristics of agents. Intelligent agents are autonomous applications that can improve system compatibility. The preliminary results indicate that the combination of time‐dependency correlation method with multiagent method is an efficient solution for brain activity recognition.

**Verdict:** _____

---

##  50. [W6892051625](https://openalex.org/W6892051625) — 2018 — preprint — `uniform`

**Concepts:** Physics (0.88), Cosmic censorship hypothesis (0.86), Black hole (networking) (0.61), Gravitational wave (0.55), Hawking radiation (0.52)

**Title:** Cosmic censorship violation in black hole collisions in higher dimensions

> We argue that cosmic censorship is violated in the collision of two black holes in high spacetime dimension D when the initial total angular momentum is sufficiently large. The two black holes merge and form an unstable bar-like horizon, which grows a neck in its middle that pinches down with diverging curvature. When D is large, the emission of gravitational radiation is strongly suppressed and cannot spin down the system to a stable rotating black hole before the neck grows. The phenomenon is demonstrated using simple numerical simulations of the effective theory in the 1/D expansion. We propose that, even though cosmic censorship is violated, the loss of predictability is small independently of D.

**Verdict:** _____

---

##  51. [W3005718018](https://openalex.org/W3005718018) — 1975 — article — `pre1990`

**Concepts:** Polarimeter (0.99), Optics (0.83), Coronagraph (0.78), Physics (0.74), Polarimetry (0.57)

**Title:** A Spectrum Scanning Stokes Polarimeter

> A photoelectric polarimeter for measuring line profiles in all four Stokes parameters has been built and operates on the SPO 40 cm coronagraph in a joint project with Sacramento Peak Observatory. A description of the optical and electronic systems and the calibration scheme is presented. Performance parameters determined from observations are also given. The polarimeter package consisting of a pair of KDP's, a quarter wave plate, and a polarizing beam splitter is located at the prime focus of the coronagraph. Modulation of the KDP's encodes polarization information into intensity signals that are electronically detected. The scanning of the spectrum, accomplished by rotating the grating, permits Stokes line profiles to be recorded on magnetic tape for processing. The instrument can be used to scan any line from 3900 to 7000 A with a spectral resolution of 0.01 A. Polarizations as small as 0.001% are detectable. The polarimeter and observing system are computer controlled.

**Verdict:** _____

---

##  52. [W2054319339](https://openalex.org/W2054319339) — 1950 — article — `pre1990`

**Concepts:** Physics (0.42), Materials science (0.34)

**Title:** Les gerbes locales de l'air et les explosions internes

> Malgré certaines apparences, les arrangements de compteurs isolés dans du plomb n'enregistrent pas des gerbes locales pénétrantes de l'air. Les effets observés sont dus à des bursts produits dans la matière et pouvant avoir une grande extension interne. La densité extérieure est étroitement liée au dispositif, elle ne provient pas de l'air mais de la matière. On retrouve le y des bursts, le parcours moyen dans l'air et le plomb des primaires et la variation de ces facteurs en fonction de la densité exigée.

**Verdict:** _____

---

##  53. [W2141380653](https://openalex.org/W2141380653) — 1982 — article — `pre1990`

**Concepts:** Symbol (formal) (0.86), Context (archaeology) (0.81), Rewriting (0.74), String (physics) (0.64), Confluence (0.48)

**Title:** Rewriting systems with limited distance forbidding context

> A random context production has a permitting and forbidding context. A symbol can be rewritten using such a production if all the permitting context symbols and no forbidding context symbol appear in the sentential string. In this paper we limit the effect of forbidding context symbols to be within a certain distance from the symbol to be rewritten. Outside this distance the forbidding context symbols do not influence the rewriting of a symbol. This restriction strictly increases the generating power of the rewriting system. A further result of this paper is a “negative parallel” version of Penttonen's normal form.

**Verdict:** _____

---

##  54. [W2159221511](https://openalex.org/W2159221511) — 1986 — article — `pre1990`

**Concepts:** Calibration (0.68), Characterization (materials science) (0.67), Dosimetry (0.64), Physics (0.55), Ionization (0.47)

**Title:** Techniques Of Absolute Low Energy X-Ray Calibration

> Recent advances in pulsed plasma research, materials science, and astrophysics have required many new diagnostic instruments for use in the low energy x-ray regime. The characterization of these instruments has provided a challenge to instrument designers and provided the momentum to improve x-ray sources and dosimetry techniques. In this paper, the present state-of-the-art in low energy x-ray characterization techniques is reviewed. A summary is given of low energy x-ray generator technology and dosimetry techniques including a discussion of thin window proportional counters and ionization chambers. A review is included of the widely used x-ray data bases and a sample of ultra-soft x-ray measuring techniques is discussed. These techniques include sub-femtoampere current measuring procedures, chopped x-ray source generators, phase sensitive detection of ultralow currents, and angular divergence measurements.

**Verdict:** _____

---

##  55. [W2077548705](https://openalex.org/W2077548705) — 1984 — article — `pre1990`

**Concepts:** Icon (0.95), Citation (0.78), Download (0.61), Computer science (0.54), Library science (0.46)

**Title:** Sometimes Independent but Never Equal: Women Teachers, 1900-1950: The Oklahoma Example

> Research Article| February 01 1984 Sometimes Independent but Never Equal: Women Teachers, 1900-1950: The Oklahoma Example Courtney Ann Vaughn-Roberson Courtney Ann Vaughn-Roberson Search for other works by this author on: This Site PubMed Google Scholar Pacific Historical Review (1984) 53 (1): 39–58. https://doi.org/10.2307/3639378 Views Icon Views Article contents Figures & tables Video Audio Supplementary Data Peer Review Share Icon Share Facebook Twitter LinkedIn MailTo Tools Icon Tools Get Permissions Cite Icon Cite Search Site Citation Courtney Ann Vaughn-Roberson; Sometimes Independent but Never Equal: Women Teachers, 1900-1950: The Oklahoma Example. Pacific Historical Review 1 February 1984; 53 (1): 39–58. doi: https://doi.org/10.2307/3639378 Download citation file: Ris (Zotero) Reference Manager EasyBib Bookends Mendeley Papers EndNote RefWorks BibTex toolbar search Search Dropdown Menu toolbar search search input Search input auto suggest filter your search All ContentPacific Historical Review Search This content is only available via PDF. Copyright 1984 The Pacific Coast Branch, American Historical Association Article PDF first page preview Close Modal You do not currently have access to this content.

**Verdict:** _____

---

##  56. [W2089243294](https://openalex.org/W2089243294) — 1966 — article — `pre1990`

**Concepts:** Plotter (0.99), Head (geology) (0.67), Computer science (0.63), Electronic circuit (0.58), Contour line (0.55)

**Title:** Contour Plotting System with High Speed Symbol Head

> An instrument for producing contour diagrams using a conventional X-Y plotter is described. It consists of a specially designed pulsed current plotting head controlled by gating circuits which use commercial analog and digital modules. The X-Y plotter scans the head over electrosensitive paper and symbols consisting of dot patterns are plotted with no mechanical delay. The gating circuits may be adjusted to any desired set of contour intervals.

**Verdict:** _____

---

##  57. [W2028760745](https://openalex.org/W2028760745) — 1981 — article — `pre1990`

**Concepts:** Cyclotron (0.81), Physics (0.69), Atomic physics (0.66), Ion (0.61), Electron (0.51)

**Title:** The relationship of field‐aligned currents to electrostatic ion cyclotron waves

> Two sources of free energy for driving ion cyclotron waves have been observed on the S3‐3 satellite: field‐aligned currents and ion beams. Since the waves are destabilized by the thermal electron drift and not the current, before correlating observations of field‐aligned currents with ion cyclotron waves, it is first necessary to determine that the current is primarily carried by thermal electrons. Comparisons of the current carried by energetic particles with the current measured by the magnetometer during several events shows that this is sometimes the case. Statistical studies indicate that the field‐aligned current density is correlated with the spectral density during ion cyclotron events. The combination of the results of this report and those of Kintner et al. (1979) is consistent with the hypothesis that the observed ion cyclotron waves are driven by a combination of ion beams and electron drift. However, the available data set does not unambiguously identify the free energy source.

**Verdict:** _____

---

##  58. [W2001348321](https://openalex.org/W2001348321) — 1985 — article — `pre1990`

**Concepts:** Physics (0.80), General relativity (0.75), Dirac (video compression format) (0.67), Einstein (0.58), Theory of relativity (0.54)

**Title:** On solutions of the Einstein-Cartan-Dirac theory

> Considers the relation between the general theory of relativity and the Einstein-Cartan theory in the case that matter is described by a Dirac field. Thereby the author finds the condition that an (arbitrary) solution of general relativity with a Dirac field is also a solution of the Einstein-Cartan-Dirac theory and vice versa. Exploiting this result the author generates new non-ghost solutions of the Einstein-Cartan-Dirac theory from ghost solutions of general relativity.

**Verdict:** _____

---

##  59. [W98538216](https://openalex.org/W98538216) — 1986 — article — `pre1990`

**Concepts:** Accreditation (0.60), Acceptance testing (0.56), Computer science (0.46), Reliability engineering (0.41), Medical physics (0.35)

**Title:** Technical evaluation of draft ANSI Standard N13. 30, ''performance criteria for radiobioassay''

> The Pacific Northwest Laboratory (PNL) is conducting a research program to evaluate the appropriateness of criteria in the ANSI draft Standard N13.30, ''Performance Criteria for Radiobioassay.'' The evaluation has progressed parallel with the preparation of the Standard by evaluating the performance of existing bioassay laboratories against the criteria specified. Recommendations for revision of the Standard and implementation of a testing/accreditation program have been formulated based on study results. The current performance testing program includes both in-vivo counting and in-vitro sample measurements. Test criteria specified in the Standard include relative bias, relative precision, and acceptable minimum detectable activity (AMDA). Results to date have indicated that the acceptance criteria in the Standard are appropriate for the existing state of the industry and are achievable by a majority of the participating laboratories. Specific conclusions are that the AMDA criteria are most difficult for the laboratories to achieve; the relative bias criterion is second in difficulty, and the precision criterion presents no problem for the laboratories; most of the participating laboratories can meet the Standard; and failure rates may decrease as the laboratories become more knowledgeable of the performance criteria. 3 refs., 11 figs., 6 tabs.

**Verdict:** _____

---

##  60. [W1974866156](https://openalex.org/W1974866156) — 1964 — article — `pre1990`

**Concepts:** Ionosphere (0.87), Geomagnetic storm (0.71), Storm (0.69), Atmospheric sciences (0.58), Geophysics (0.55)

**Title:** Morphology of Storms in the Ionosphere

> A review is given on the morphology of storms in the ionosphere based on the results obtained during the world-wide cooperative observations, IGY (1957-1958) and IGC (1959). Ionospheric disturbances are classified into two categories: disturbances that take place in the lower ionosphere and F region ionospheric storms.E region disturbances are mainly caused by an abnormal ionizing agent penetrating into the lower ionosphere. Sudden ionospheric disturbances are due to an outburst of solar X rays associated with chromospheric flares, while polar blackout phenomena are produced by incoming energetic particles. It is shown that solar cosmic ray particles (sub-relativistic) ejected from an intense flare are the source of a prolonged blackout in the polar cap region, known as polar cap absorption, and auroral particles consisting presumably of energetic electrons are responsible for auroral blackouts. Average features of these two types of polar blackout are described in some detail with other related geophysical phenomena.F region storms accompanying large electron density variations are closely connected with geomagnetic storms. The disturbances are world-wide, their features being markedly different both with respect to geomagnetic storm-time as well as time of day. The general morphological features of storms are, therefore, described in terms of the storm-time variation, Dst, and the disturbance diurnal variation, Ds. A theoretical interpretation of ionospheric F2 storms is still incomplete; however, two dominant theories which may explain the main features of electron density variations are discussed in the light of recent knowledge of the ionosphere. It is concluded that the Dst variation may be produced by the effect of thermal heating of the ionosphere during storms, whereas the Ds variation may be related in some way to electrodynamical drift motions of electrons due to the interaction of the geomagnetic field with the electric field induced by the enhanced dynamo-action in the ionosphere. Other disturbance effects in the F region and their connection with exospheric phenomena are also discussed briefly.

**Verdict:** _____

---

##  61. [W1481809268](https://openalex.org/W1481809268) — 1982 — article — `pre1990`

**Concepts:** Respite care (0.71), Transport engineering (0.64), Intrusion (0.52), Control (management) (0.50), Traffic volume (0.45)

**Title:** Controlling vehicle speeds on local streets

> Engineers and planners have realised that traffic volume is not the only component of traffic intrusion problems in residential areas; rather these problems are multi-dimensional. Vehicle speed is one of these additional dimensions. Residents have also demonstrated an unwillingness to greatly sacrifice their personal mobility to gain respite from traffic intrusion. Thus there has been a shift in local area planning from measures such as street closures to the use of devices for speed control (e. g. humps, narrowings, chicanes and roundabouts), and the imposition of special speed limits. This note provides some initial steps towards the formal definition of local area traffic planning objectives, and introduces some possible mathematical models. Language: en

**Verdict:** _____

---

##  62. [W621378406](https://openalex.org/W621378406) — 1980 — article — `pre1990`

**Concepts:** Fuel efficiency (0.75), Intersection (aeronautics) (0.74), Automotive engineering (0.50), Transport engineering (0.48), Traffic signal (0.47)

**Title:** Fuel consumption at isolated traffic signals

> Traditionally the phase split and cycle length of traffic signals at isolated intersections have been set so as to minimise the total delay experienced by the vehicles passing through the intersection. This often means that a moving traffic stream is interrupted to allow waiting vehicles in an opposing stream to proceed. The effect of stopping a vehicle which is travelling at 60 km/h is shown to be the equivalent of delaying a stationary vehicle by approximately an extra 67 seconds. This paper analyses the effect on fuel consumption of varying the cycle length of traffic signals at two isolated intersections for various traffic conditions using a model. It shows that some savings may be obtained in light traffic conditions, while there may be little advantage in modifying cycle length in medium to heavy conditions. The costs of the increased delays that are imposed on motorists when the cycle length is increased are related to the reduced fuel consumption and vehicle operating costs that are achieved under these conditions. The largest potential community benefit appears to be when traffic conditions are relatively light, particularly where the flows on the minor streets are small (a). This paper is no 80021.

**Verdict:** _____

---

##  63. [W2048608413](https://openalex.org/W2048608413) — 1964 — article — `pre1990`

**Concepts:** Newton's laws of motion (0.88), Law (0.66), Physics (0.64), Impulse (physics) (0.63), Interpretation (philosophy) (0.52)

**Title:** Newton's Laws of Motion and the 17th Century Laws of Impact

> A number of writers on history of science have made it clear that in using the term “motive force” in the “Principia,” Newton referred to what we now call “impulse.” With this interpretation, there is a simple and plausible connection between the laws of impact as they were known and described in Newton's day and Newton's formulation of the Laws of Motion in the “Principia,” and we speculate that Newton might have been motivated by such a perception.

**Verdict:** _____

---

##  64. [W1978562932](https://openalex.org/W1978562932) — 1983 — article — `pre1990`

**Concepts:** Modal analysis using FEM (0.75), Modal (0.74), Eigenvalues and eigenvectors (0.66), Normal mode (0.62), Computation (0.57)

**Title:** Method for Improving Incomplete Modal Coupling

> The writers are concerned with the free vibration of discrete undamped linear dynamic systems commonly designed in structural engineering. The primary purpose is to present a rational method for improving the natural modes and frequencies computed by incomplete modal coupling, without increasing the order of the resultant eigenvalue problem. Improvement is accomplished through use of a candidate table in an iterative process that introduces significant modes into sequential modal analyses. The error trend and sensitivity analysis due to modal truncation is evaluated by computation of a scalar number called significance index which represents an approximation to the error in a certain eigenvalue due to omission of a certain mode shape. This information forms the basis of the candidate table, which serves as a guide for the optimal automated selection of modes for modal substitution. The method of analysis is demonstrated for a discrete model containing 378 degrees‐of‐freedom.

**Verdict:** _____

---

##  65. [W2009163785](https://openalex.org/W2009163785) — 1986 — article — `pre1990`

**Concepts:** Formant (0.83), Bridging (networking) (0.77), Computer science (0.56), Linguistics (0.51), Joint (building) (0.48)

**Title:** Notes by a film‐maker

> Abstract For a number of years the author has been occupied with the investigation of movements of the mouth and the accompanying speech sounds of Dutch interjections with the purpose of synthesizing with a computer the sounds and images for a video film of “speaking heads”. In this article some aspects of speech synthesis are touched upon which can be realized with the help of the MIDIM/ VOSIM‐system. The phenomena of the ‘auditive pause’, the so‐called ‘joint’ for bridging quick and strong formant springs and the analysis and synthesis (via D‐comprehensors) of vowels in the interjections are also shown.

**Verdict:** _____

---

##  66. [W1539568082](https://openalex.org/W1539568082) — 1976 — article — `pre1990`

**Concepts:** Algorithm (0.65), Annotation (0.54), Computer science (0.49), Artificial intelligence (0.45), Type (biology) (0.42)

**Title:** Some special decompositions of 𝐸³

> A great deal of attention has been given to the question: which upper semicontinuous decompositions of <inline-formula content-type="math/mathml"> <mml:math xmlns:mml="http://www.w3.org/1998/Math/MathML" alttext="upper E cubed"> <mml:semantics> <mml:mrow class="MJX-TeXAtom-ORD"> <mml:msup> <mml:mi>E</mml:mi> <mml:mn>3</mml:mn> </mml:msup> </mml:mrow> <mml:annotation encoding="application/x-tex">{E^3}</mml:annotation> </mml:semantics> </mml:math> </inline-formula> into pointlike continua give <inline-formula content-type="math/mathml"> <mml:math xmlns:mml="http://www.w3.org/1998/Math/MathML" alttext="upper E cubed"> <mml:semantics> <mml:mrow class="MJX-TeXAtom-ORD"> <mml:msup> <mml:mi>E</mml:mi> <mml:mn>3</mml:mn> </mml:msup> </mml:mrow> <mml:annotation encoding="application/x-tex">{E^3}</mml:annotation> </mml:semantics> </mml:math> </inline-formula>. It has recently been determined that some decompositions of <inline-formula content-type="math/mathml"> <mml:math xmlns:mml="http://www.w3.org/1998/Math/MathML" alttext="upper E cubed"> <mml:semantics> <mml:mrow class="MJX-TeXAtom-ORD"> <mml:msup> <mml:mi>E</mml:mi> <mml:mn>3</mml:mn> </mml:msup> </mml:mrow> <mml:annotation encoding="application/x-tex">{E^3}</mml:annotation> </mml:semantics> </mml:math> </inline-formula> into points and straight line segments give decomposition spaces which are topologically distinct from <inline-formula content-type="math/mathml"> <mml:math xmlns:mml="http://www.w3.org/1998/Math/MathML" alttext="upper E cubed"> <mml:semantics> <mml:mrow class="MJX-TeXAtom-ORD"> <mml:msup> <mml:mi>E</mml:mi> <mml:mn>3</mml:mn> </mml:msup> </mml:mrow> <mml:annotation encoding="application/x-tex">{E^3}</mml:annotation> </mml:semantics> </mml:math> </inline-formula>. In this paper we apply a new condition to the set of nondegenerate elements of a decomposition which enables one to conclude that the resulting decomposition space is homeomorphic to <inline-formula content-type="math/mathml"> <mml:math xmlns:mml="http://www.w3.org/1998/Math/MathML" alttext="upper E cubed"> <mml:semantics> <mml:mrow class="MJX-TeXAtom-ORD"> <mml:msup> <mml:mi>E</mml:mi> <mml:mn>3</mml:mn> </mml:msup> </mml:mrow> <mml:annotation encoding="application/x-tex">{E^3}</mml:annotation> </mml:semantics> </mml:math> </inline-formula>.

**Verdict:** _____

---

##  67. [W4233978712](https://openalex.org/W4233978712) — 1987 — report — `pre1990`

**Concepts:** Physics (0.90), Hadron (0.69), Pion (0.68), Annihilation (0.56), Particle physics (0.43)

**Title:** Bose-Einstein correlations in e/sup +/e/sup -/ collisions

> The MARK II detector is used to study the Bose-Einstein correlation between pairs and triplets of charged pions produced in hadronic decays of the J)psi), the ..sqrt..s = 4 to 7 GeV continuum above the J)psi), two photon events at ..sqrt..s = 29 GeV, and e/sup )plus/)e/sup )minus/) annihilation events at ..sqrt..s = 29 GeV as a function of Q/sup 2/, the four-momentum transfer squared. After corrections for Coulomb effects and pion misidentification, we find a nearly full Bose-Einstein enhancement ..cap alpha.. in the J)psi) and the two photon data and about half the maximum value in the other two data sets. The radius parameter )tau)(an average over space and time) given by pion pair analyses lies within a band of +-0.10 fm around 0.73 fm and is the same, within errors, for all four data sets. Pion triplet analyses also give a consistent radius of approx. 0.54 fm. fits to two-dimensional distributions R(q/sub T//sup 2/, q/sub C//sup 2/) of invariant components of Q/sup 2/ = q/sub T//sup 2/ )plus) q/sub C//sup 2/ give )tau)/sub T/ approx. )tau)C approx. )tau), where q/sub T/ is the transverse three-momentum difference calculated with respect to the net pair three-momentum, and q/sub C/ is in effect the longitudinal three-momentum difference in the pion pair rest frame. When q/sub T/ is calculated with respect to the jet axis for two-jet events in the e/sup )plus/)e/sup )minus/) annihilation data at ..sqrt..s = 29 GeV, a fit to R(q/sub T//sup 2/, q/sub C//sup 2/) also gives )tau)/sub T/ approx. )tau)/sub C/ approx. )tau). Noting that q/sub L/ and q/sub 0/ are not invariant, we make fits to R(/sub T//sup T/, q/sub L//sup 2/) and to R(q/sub T//sup 2/, q/sub 0//sup 2/) (Kopylov formulation), and we find )tau)/sub 0/ approx. )tau)/sub L/ approx. )23))tau)/sub T/ to )12))tau)/sub T/. 44 refs., 43 figs., 15 tabs

**Verdict:** _____

---

##  68. [W4235559521](https://openalex.org/W4235559521) — 1972 — dissertation — `pre1990`

**Concepts:** Nonlinear system (0.87), A priori and a posteriori (0.74), Identification (biology) (0.63), Nonlinear system identification (0.61), System identification (0.60)

**Title:** Maximum likelihood identification of nonlinear systems.

> Maximum likelihood technique 1s used to estimate the parameters of single input single output nonlinear systems. Two algorithms are described and applied . One is for the identification of Hammerstein nonlinear models, which is useful if no priori knowledge about the mathematical form of the nonlinearity is available. The other algorithm is for the identification of systems which have known forms for the nonlinearities. It is derived for continuous nonlinear systems, and applied for simulated data generated from linear and nonlinear second order continuous models. It is also used to fit linear, and nonlinear second order continuous models to practical data taken from a test on the glucose homeostatic control system of dogs. The emphasis is on obtaining simplified algorithm for continuous nonlinear systems in order to save computing time, and get satisfactory results.

**Verdict:** _____

---

##  69. [W119805742](https://openalex.org/W119805742) — 1983 — article — `pre1990`

**Concepts:** Magnetohydrodynamics (0.80), Physics (0.68), Flute (0.62), Dissipative system (0.62), Instability (0.59)

**Title:** Flute instability in an open min B system

> In a confinement system with an average min B, in part of which the particles undergo an unfavorable magnetic drift, the familiar MHD flute waves may be accompanied by some natural flute waves with an azimuthal phase velocity on the order of or smaller than the magnetic drift velocity of the ions in the region of favorable curvature. This wave branch is not described in the MHD approximation; it arises in the two-fluid model. These waves have a negative energy and may thus be excited by dissipative effects.

**Verdict:** _____

---

##  70. [W2342437579](https://openalex.org/W2342437579) — 1978 — article — `pre1990`

**Concepts:** Computer science (0.65), Vocational education (0.62), Linear programming (0.59), Manpower planning (0.57), Investment (military) (0.57)

**Title:** Models for Educational and Manpower Planning: A Dynamic Linear Programming Approach

> The purpose of this paper is to show that many optimization problems for educational and manpower planning models can be written in a standard dynamic linear programming form. A basic model of educational planning is described and extensions of the model (investment and vocational training submodels and a three level educational model) are given. \n\nWhen describing models, two basic models are singled out using two different controls: recruitment in the first and promotion in the second. Finally, an integrated model of economy-manpower interaction is considered. \n\nThe possibilities and limitations of DLP as applied to manpower and educational planning problems are discussed.

**Verdict:** _____

---

##  71. [W2151004606](https://openalex.org/W2151004606) — 1972 — article — `pre1990`

**Concepts:** Isotropy (0.77), Physics (0.75), Vorticity (0.74), Angular velocity (0.69), Turbulence (0.57)

**Title:** A note on the angular dispersion of a fluid line element in isotropic turbulence

> The mean-square angular displacement of a fluid material line element is expressed as an integral of the corresponding angular velocity in material coordinates, with forms like those in Taylor's (1921) linear displacement analysis. Measurements using a hydrogen-bubble tracer in isotropic turbulence show that the mean-square angular velocity of a line is of the same order of magnitude as the mean-square vorticity, and that its ‘Lagrangian’ integral time scale is of the order of the inverse of the r.m.s. vorticity. The angular velocity of a line element is also formulated in spatial co-ordinates. Finally, the connexion between angular dispersion and the approach toward isotropy is pointed out.

**Verdict:** _____

---

##  72. [W2060959612](https://openalex.org/W2060959612) — 1988 — article — `pre1990`

**Concepts:** Physics (0.70), Mixing (physics) (0.66), Photorefractive effect (0.65), Optics (0.61), Holography (0.60)

**Title:** Anisotropic four-wave mixing in cubic photorefractive crystals

> The anisotropic four-wave mixing in the scheme recently proposed by S.I. Stepanov and M.P. Petrov (Opt. Commun. vol.53, p.64-8, 1985) is studied. The main feature of this interaction arrangement is that the same phase hologram (index grating) has opposite contrasts for orthogonally polarized, counterpropagating waves. The coupled nonlinear equations, in the case of transmission and reflection gratings, for the pi /2 photorefractive phase shift are exactly solved, and their properties are discussed in detail. The numerical evidence of the effects of bistability and self-oscillation is included.< <ETX xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink">&gt;</ETX>

**Verdict:** _____

---

##  73. [W4303078340](https://openalex.org/W4303078340) — 1915 — article — `pre1990`

**Concepts:** Icon (0.97), Citation (0.57), Download (0.54), Information retrieval (0.45), Computer science (0.43)

**Title:** The Belgian Soldier

> Essay| March 01 1915 The Belgian Soldier Current History (1915) 1 (6): 1215–1216. https://doi.org/10.1525/curh.1915.1.6.1215 Views Icon Views Article contents Figures & tables Video Audio Supplementary Data Peer Review Share Icon Share Twitter LinkedIn Tools Icon Tools Get Permissions Cite Icon Cite Search Site Citation The Belgian Soldier. Current History 1 March 1915; 1 (6): 1215–1216. doi: https://doi.org/10.1525/curh.1915.1.6.1215 Download citation file: Ris (Zotero) Reference Manager EasyBib Bookends Mendeley Papers EndNote RefWorks BibTex toolbar search Search Dropdown Menu toolbar search search input Search input auto suggest filter your search All ContentCurrent History Search This content is only available via PDF. © 1915 by The Regents of the University of California1915 Article PDF first page preview Close Modal You do not currently have access to this content.

**Verdict:** _____

---

##  74. [W2571345580](https://openalex.org/W2571345580) — 1983 — article — `pre1990`

**Concepts:** Physics (0.88), Planetary nebula (0.76), Astrophysics (0.69), Photometry (optics) (0.57), Astronomy (0.50)

**Title:** Two-dimensional photometry of planetary nebulae

> In connection with the study of planetary nebulae, problems still exist in understanding such basic properties as three-dimensional structure, optical opacity to the central star's ionizing flux, and electron temperature and electron density variations within the nebular gas. To study these properties, two-dimensional images taken in many spectral lines are required. However, such a study presents a formidable problem in data analysis. In the present investigation, an attempt has been made to overcome the difficulties by using an imaging system which encodes the data digitally. Calibrated intensity maps could be constructed to test models of ionization structure and to produce two-dimensional maps of electron temperature and density. Both the results of a uniform-shell test and the nature of the solutions for the volume emissivity were found to support a nebular model in which the bright ring is part of a closed shell of variable density that resembles the torus proposed by Minkowski and Osterbrock (1960).

**Verdict:** _____

---

##  75. [W2015584011](https://openalex.org/W2015584011) — 1971 — article — `pre1990`

**Concepts:** Tensor field (0.72), Invariant (physics) (0.67), Lorentz group (0.65), Symmetric tensor (0.54), Mathematics (0.54)

**Title:** Invariant Tensor Fields in Physics and the Classical Groups

> The relativistic S-matrix with spin transforms as an invariant tensor under the action of the homogeneous Lorentz group. This transformation property enables one to analyze the structure of the S-matrix from the viewpoint of group theory. Here this procedure is generalized and applied to tensor fields which are invariant under one of the classical groups. In each case the number of linearly independent tensor fields on a given orbit is determined. The results may be useful in particle physics.

**Verdict:** _____

---

##  76. [W160089336](https://openalex.org/W160089336) — 1975 — article — `pre1990`

**Concepts:** Sampling (signal processing) (0.77), Computer science (0.58), Quality (philosophy) (0.56), Process (computing) (0.54), Simple random sample (0.51)

**Title:** Sampling from Batches

> The outputs of many manufacturing processes consist of batches which tend to be more homogeneous than the outputs from the process as a whole. Thus the quality of just one batch is not necessarily representative of the long term quality of the process. This paper discusses a two stage plan for obtaining representative samples of the outputs of such manufacturing processes. The two stage plan is both more efficient and more convenient than simple random sampling. The plan entails sampling k of the batches and subsampling m units within each of the sampled batches. Formulas are presented which determine how k and m should be chosen to maximize the sampling precision subject to cost constraints. Several numerical examples illustrate the adverse effect on precision due to sampling from too few batches. In particular it is shown that drawing the entire sample from just one batch leads to very poor precision.

**Verdict:** _____

---

##  77. [W2063964227](https://openalex.org/W2063964227) — 1984 — article — `pre1990`

**Concepts:** Optical fiber (0.45), Computer science (0.42), Telecommunications (0.24)

**Title:** Measuring method for optical fibre sensors

> A new measuring method for the signal amplitude in intensity modulating fibre optic sensors is described. A reference signal is generated in the time domain. The method is insensitive for the sensitivity fluctuations of the light transmitter and the light receiver. The method is experimentally tested. It is shown how the method can be used to measure the intensity attenuation in a fibre optic microbend sensor.

**Verdict:** _____

---

##  78. [W2767151332](https://openalex.org/W2767151332) — 1983 — article — `pre1990`

**Concepts:** Computer science (0.45), Engineering (0.42), Engineering drawing (0.41), Mechanical engineering (0.40), Automotive engineering (0.38)

**Title:** Design And Calculation Methods For High-Speed Gears Of Advanced Technology.

> High-speed gears of very high powers and/or very high speeds must be exactly analyzed and optimized in gearing, bearing and housing in order to achieve low noise, low vibra tion running with maximum safety in operation.The gearing must be checked by detailed calculations in load capacity, including an exact analysis of the scoring safety.Special design means must be applied in order to cover thermal problems at the gearing.Besides this, the calculation and design of the plain bear ings are of main interest.They also must be analyzed in detail, not only in general hydrodynamic load capacity, but also in their real temperature and pressure conditions in the oil film.The design of the plain bearing then has to be adapted to its vibration behaviour.Using modern CAE methods, the design process can be made faster and safer.Practical examples of some of the highest-powered high-speed gears of the world prove the methods used in design, calculations and manufacturii).g.

**Verdict:** _____

---

##  79. [W1972608881](https://openalex.org/W1972608881) — 1986 — article — `pre1990`

**Concepts:** Liquid crystal (0.77), Metastability (0.68), Continuum hypothesis (0.54), Limit (mathematics) (0.54), Physics (0.53)

**Title:** Bogolyubov-Tyablikov-like approximation for nematic liquid crystals: Bridge between continuum and mean-field theories

> A procedure analogous to the Bogolyubov-Tyablikov approximation is proposed in order to bridge between the continuum theory and the Maier-Saupe model of nematic liquid crystals. The equation obtained for the order parameter, which results in a first-order transition, reduces to the Maier-Saupe equation in the limit of infinite-range interactions. A prescription for the evaluation of the free energy in the framework of the Bogolyubov-Tyablikov treatment is presented, and the resulting Maxwell construction is used to determine the first-order transition temperature. The transition temperature, the range of metastability, and the value of the order parameter at the transition are all considerably lower than in Maier-Saupe theory.

**Verdict:** _____

---

##  80. [W4242422561](https://openalex.org/W4242422561) — 1967 — article — `pre1990`

**Concepts:** Vibration (0.79), Impulse (physics) (0.59), Natural frequency (0.50), Femur (0.50), Acoustics (0.44)

**Title:** On a Bone-Vibration

> This experiment is one step to clarify dynamic mechanical properties of bones, especially femurs.Material: four dry femurs.We designed a method that a mechanical impulse was exerted on a femoral head along the functional axis of femur with a pendulum. Then a femur, whose condyle is fixed and head is free, is placed horizontally.When a mechanical impulse was exerted on a femur in the above position, a bone vibration was developed. This vibration was analyzed, and was similar to a summation of a high- and a low-frequency component. Therefore, we picked out separately the high- and the low-frequency component with a filter circuit. There were vibrations with logarithmic decrement. The vibrations had a natural frequency themselves—the high was about 500cps and the low was about 100cps.Now, a solution of a sort of a second-order differential equation Md2x/dt2+Sdx/dt+Kx=F(t)is also a damping vibration with logarithmic decrement. Then, we added two second-order differential equations with two different constant coefficients, using a desk-top ANALOG computor. Using this solution yielded a similar wave to a bone vibration.Therefore, we think now that a bone vibration under the above conditions may be expressed as a summation of two ordinary second-order differential equations.Furthermore, analysing many more bone-vibrations, we will compare the difference of the damping ratio and the natural frequency of vibration between many bones.

**Verdict:** _____

---

##  81. [W2032059802](https://openalex.org/W2032059802) — 1969 — article — `pre1990`

**Concepts:** Parallax (0.93), Physics (0.85), Binary number (0.54), Computer vision (0.40), Artificial intelligence (0.37)

**Title:** Parallax and mass ratio of the visual binary BD +4 4510.

> Search Bar to Enter New Query quick field: Author First Author Abstract Year Fulltext Select a field or operator abstract abstract only acknowledgements affiliation arXiv category author count author bibcode bibliographic group bib abbrev, e.g. ApJ body of article data archive collection citation count doctype doi entdate first author fulltext identifier inst keyword object orcid page property publication full name date published title volume year citations() pos() references() reviews() similar() topn() trending() useful() single wildcard: ? wildcard: * exact match: = All Search Terms Your search returned 0 results Your search returned 0 results

**Verdict:** _____

---

##  82. [W2085929438](https://openalex.org/W2085929438) — 1970 — article — `pre1990`

**Concepts:** Physics (0.81), Boson (0.73), Fermion (0.71), Gravitation (0.63), Theory of relativity (0.45)

**Title:** Relativistic Systems of Particles in Gravitational Interaction

> An elementary heuristic discussion of relativistic systems of particles in mutual gravitational interaction is given. Both in the boson and fermion cases, the main features of rigorous treatments are very simply recovered. A conceptual dilemma touching the use of various coordinate systems in such considerations is clarified. Finally, it is shown that in any realistic boson system, the relativistic effects of gravitation are probably masked by the other fundamental interactions, in contradistinction with fermion systems.

**Verdict:** _____

---

##  83. [W2104225190](https://openalex.org/W2104225190) — 1979 — article — `pre1990`

**Concepts:** Microstrip antenna (0.73), Microstrip (0.58), Radiation pattern (0.56), Radiation (0.50), Physics (0.49)

**Title:** A model for calculating the radiation field of microstrip antennas

> Starting from the equivalence principle, an aperture model is developed for calculating the radiation field of microstrip antennas. In this communication the model is applied to the rectangular microstrip resonator antenna. Antenna characteristics, like patterns and radiation resistance, are computed and compared with experimental results. The model and the calculations include the higher order modes as well as the fundamental mode of the resonator antenna.

**Verdict:** _____

---

##  84. [W1482436422](https://openalex.org/W1482436422) — 1971 — article — `pre1990`

**Concepts:** Physics (0.68), Spurious relationship (0.68), Nonlinear system (0.66), Quadrupole (0.66), Scattering (0.65)

**Title:** OBSERVATIONS OF NONLINEAR SCATTERING FROM A PLASMA COLUMN.

> Nonlinear interaction effects are considered for signals incident on an unmagnetized cold plasma column, without making the quasi-static approximation. It is found that the nonlinearly generated quadrupole component is only modified slightly and that no multipolar component can give a forward- or back-scattered signal. However, strong nonlinear forward scattering was observed in previous experiments. This spurious result has been traced to the effect of the earth's magnetic field. When this is cancelled, predominantly quadrupolar radiation is observed, in agreement with theory.

**Verdict:** _____

---

##  85. [W4256729226](https://openalex.org/W4256729226) — 1988 — article — `pre1990`

**Concepts:** Productivity (0.77), Computer science (0.63), Work (physics) (0.60), Service (business) (0.49), Office automation (0.48)

**Title:** Computers' impact on productivity and work life

> Rapid spread of computer and telecommunication technologies throughout white-collar work has forced researchers to consider their impacts on the people who use them. The present study uses a multi-method, lagged, time-series design to examine the impact of a computerized record system on the work life of customer service representatives in a large utility company. Results show that the computer technology had mixed effects in terms of both productivity and quality of working life, and that these effects varied depending on local organizational culture, management quality, type of worker and their detailed work tasks. Furthermore, during the year in which the computer system was being introduced, the computer system itself, its methods of use, and the managerial goals that spawned it all evolved in response to workers and other factors. These results are used to illustrate the conceptual and methodological complexities involved in establishing the causal impact of computer technology, and to suggest alternate methods for thinking about and measuring technological impact.

**Verdict:** _____

---

##  86. [W2033143906](https://openalex.org/W2033143906) — 1983 — article — `pre1990`

**Concepts:** Actuary (0.79), Computer science (0.54), Business (0.19), Finance (0.11)

**Title:** A day in the life of a new-generation computer user

> This is a fictional account of how the next generation of computers might help a user on a typical day in 1993. All technologies mentioned have already been demonstrated as research prototypes; only the specific machines and situations are fictional projections. In the scenario, the user, John Atarashi, is an actuary working for a company that develops retirement benefit plans for client companies around the world.

**Verdict:** FLAG: BORDERLINE (likely wrong field; has some overlap with CS but fringe)

---

##  87. [W2007687569](https://openalex.org/W2007687569) — 1987 — article — `pre1990`

**Concepts:** Physics (0.91), Astrophysics (0.67), Shock wave (0.64), Radiative cooling (0.61), Star formation (0.60)

**Title:** Hydrogen molecules and the radiative cooling of pregalactic shocks

> The nonequilibrium radiative cooling, recombination, and molecule formation behind steady state shock waves in a gas of primordial composition have been calculated in detail for a number of cases. The authors have solved the rate equations for these processes, together with the hydrodynamical conservation equations. Such shock waves are relevant to a wide range of theories of galaxy and pregalactic star formation. A purely atomic gas of H and He which is shock-heated to temperatures above 10<SUP>4</SUP>K is assumed. The results indicate that formation of H<SUB>2</SUB> molecules in the post-shock gas may be quite common for a significant range of shock velocities. The extra cooling resulting from H<SUB>2</SUB> formation greatly reduces previous estimates of the characteristic gravitational scale length and the characteristic mass subject to gravitational instability in these postshock regions.

**Verdict:** OK

---

##  88. [W2065268273](https://openalex.org/W2065268273) — 1972 — article — `pre1990`

**Concepts:** Course (navigation) (0.75), Mathematics education (0.71), Subject matter (0.60), Computer science (0.49), Calculus (dental) (0.45)

**Title:** A Special Topics Course in Perturbation Methods

> A special topics course dealing with perturbation methods in applied mathematics which was recently taught at Stevens Institute of Technology is described. Since the course enrolment was comprised of undergraduate and graduate mathematics students as well as graduate students in engineering, an unusual course philosophy had to be developed and implemented. The approach taken to achieve this in both teaching techniques and selection of subject matter is discussed in detail. Finally, conclusions are drawn from the students’ and the instructor's experiences with the course which hopefully will be of value to those considering offering special topics courses in the future.

**Verdict:** OK

---

##  89. [W2063253559](https://openalex.org/W2063253559) — 1977 — article — `pre1990`

**Concepts:** Beryllium (0.83), Atomic physics (0.72), Quadrupole (0.70), Physics (0.63), Eigenfunction (0.59)

**Title:** Magnetic quadrupole transition probabilities for the beryllium isoelectronic sequence

> The magnetic quadrupole transition probabilities for the $1{s}^{2}2s2p$ $^{3}P_{2}\ensuremath{-}1{s}^{2}2{s}^{2}$ $^{1}S_{0}$ and $1{s}^{2}2s2p$ $^{3}P_{2}\ensuremath{-}1{s}^{2}2{p}^{2}$ $^{1}S_{0}$ transitions of elements of the beryllium isoelectronic sequence are calculated using eigenfunctions obtained by the $Z$-expansion method. Matrix elements are presented for $Z=6\ensuremath{-}30$ and transition probabilities are obtained for all elements with $Z\ensuremath{\ge}6$ for which excitation energies are available. Good agreement is obtained with other calculations when common values for the transition energies are used.

**Verdict:** OK

---

##  90. [W2013296035](https://openalex.org/W2013296035) — 1984 — article — `pre1990`

**Concepts:** Physics (0.56), Irreducible representation (0.49), Combinatorics (0.49), Isoscalar (0.43), Product (mathematics) (0.43)

**Title:** Coefficients of fractional parentage for U(m + p/n + q) ⊃ U(m/n) × U(p/q) and U(m/n) ⊃ U(m) × U(n)

> The outer-product reduction coefficients (ORC) which reduce the representation (rep) induced from the irreps of the permutation groups S(f1) and S(f2) into the irreps of S(f1 + f2) are shown to be the 'indirect coupling' coefficients for the U(m + p/n + q) ⊃ U(m/n) × U(p/q) irreducible basis. The non-standard ORC for reducing the rep induced from the non-standard irreps of S(f13) ⊃ S(f1) × S(f3) and S(f24) ⊃ S(f2) × S(f4) into that of S(f) ⊃ S(f12) × S(f34), with fij = fi + fj, f = f12 + f34, are identified with the U(f) ⊃ U(f12) × U(f34) Clebsch-Gordan coefficient for the special Gel'fand bases of U(f12) and U(f34). The U(m + p/n + q) ⊃ U(m/n) × U(p/q) CFP, as well as its special case the U(m+p) ⊃ U(m) × U(p) CFP, are identified with the S(f) ⊃ S(f12) × S(f34) outer-product isoscalar factor. The U(m/n) ⊃ U(m) × U(n) CFP are obtained from the U(m + n) ⊃ U(m) × U(n) CFP by simply changing all the partition labels for U(n) into their conjugates (interchanging rows with columns) and taking into account a phase change. The CFP can be calculated from the ORC. Numerical values of the one-body CFP for systems with up to six particles are tabulated.

**Verdict:** OK

---

##  91. [W2054753273](https://openalex.org/W2054753273) — 1980 — article — `pre1990`

**Concepts:** Rhetorical question (0.74), Technical writing (0.71), Term (time) (0.70), Meaning (existential) (0.69), Process (computing) (0.67)

**Title:** Definition: The First Step in the Thinking/Writing Process

> Practicing the forms of definitions may not produce writing that satisfies the informational needs of readers. This paper discusses definition as a method for engaging students in the process by which thinking and writing test and clarify one another. By first saying all he can about the theoretical and practical meaning of a term, the student can analyze his writing to discover the significances the term has for different readers and the rhetorical devices that best express the meanings. The writer then can compose a series of redefinitions of the term for different readers according to their needs.

**Verdict:** FLAG: WRONG_FIELD 

---

##  92. [W4236980170](https://openalex.org/W4236980170) — 1985 — article — `pre1990`

**Concepts:** Very-large-scale integration (0.94), Computer science (0.66), Residue number system (0.60), Code (set theory) (0.49), Residue (chemistry) (0.44)

**Title:** Low-cost residue codes and their application to self-checking VLSI systems

> The efficient application of error-detecting codes to VLSI designs requires a study of their cost and effectiveness to supplement the knowledge of their theoretical properties. The paper discusses the tradeoffs for a low-cost residue code applied to common types of VLSI hardware. Comparisons are made between the kinds of residue codes available and their suitability for use in VLSI designs. The code is then applied to a typical VLSI system for comparison with other test strategies.

**Verdict:** FLAG_BORDERLINE (almost OK for both physics as well as CS/math but clear connection is hazy)

---

##  93. [W2186825090](https://openalex.org/W2186825090) — 1985 — article — `pre1990`

**Concepts:** Leakage (economics) (0.68), Resonator (0.68), Optics (0.47), Physics (0.40), Materials science (0.40)

**Title:** METHOD FOR LEAKY WAVEGUIDES

> In this novel cavity resonator method for measuring the phase and leakage constants of leaky waveguidesr power is sent in transversely, in a reversal of the leakage process itself. The cavity therefore requires no coupling holes, and the method is accurate and convenient to use, as shown in an illustrative example.

**Verdict:** OK

---

##  94. [W2019469205](https://openalex.org/W2019469205) — 1985 — article — `pre1990`

**Concepts:** Citation (0.77), Computer science (0.70), Code (set theory) (0.64), Corporation (0.60), Generator (circuit theory) (0.56)

**Title:** A unified code generator for multiple architectures

> Article Free Access Share on A unified code generator for multiple architectures Author: Sarah Rymal McKie Sperry corporation, Roseville, Minnesota Sperry corporation, Roseville, MinnesotaView Profile Authors Info & Claims ACM '85: Proceedings of the 1985 ACM annual conference on The range of computing : mid-80's perspective: mid-80's perspectiveOctober 1985 Pages 412–416https://doi.org/10.1145/320435.320552Online:01 October 1985Publication History 0citation101DownloadsMetricsTotal Citations0Total Downloads101Last 12 Months2Last 6 weeks1 Get Citation AlertsNew Citation Alert added!This alert has been successfully added and will be sent to:You will be notified whenever a record that you have chosen has been cited.To manage your alert preferences, click on the button below.Manage my AlertsNew Citation Alert!Please log in to your account Save to BinderSave to BinderCreate a New BinderNameCancelCreateExport CitationPublisher SiteeReaderPDF

**Verdict:** OK (but the abstract present here itself is junk)

---

##  95. [W2151210328](https://openalex.org/W2151210328) — 1985 — article — `pre1990`

**Concepts:** Ozone (0.63), Radiative transfer (0.61), Perturbation (astronomy) (0.53), Convection (0.52), Atmospheric chemistry (0.50)

**Title:** A coupled one‐dimensional radiative‐convective, chemistry‐transport model of the atmosphere: 1. Model structure and steady state perturbation calculations

> An atmosphere model composed of a narrow band radiative‐convective (RC) code coupled with a one‐dimensional chemistry and transport code is described. The RC model, formulated in log‐pressure coordinates, includes accurate solar absorption calculations for O 3 , O 2 , H 2 O, and CO 2 . Infrared heating and cooling by CO 2 , O 3 , and H 2 O are calculated with a narrow band formulation, while broader band formulations are used for CH 4 , N 2 O, CFC 11, and CFC 12. The atmospheric chemistry and transport model uses photochemical reaction rate data from Jet Propulsion Laboratory publication 82–57. The calculated steady state atmospheric response to several potential perturbations is discussed. Doubling the atmospheric CO 2 level yields a change in total ozone of +2.9% and a surface temperature increase of 1.7 K. The continued release of chlorofluorocarbons (CFC's) alone at nominal rates gives a calculated column ozone change of −5.7% at steady state, while for a combined 2×CO 2 +CFC perturbation the result is −3.5%. Ozone perturbations due to increases in N 2 O, CH 4 , and aircraft are also discussed. Two coupled scenarios including projected changes that may occur in about 100 years due to all these identified man‐made perturbations are discussed. The calculated ozone column changes are −4.5% and +1.5%, assuming fixed and doubled methane source strengths, respectively.

**Verdict:** OK

---

##  96. [W1990743634](https://openalex.org/W1990743634) — 1988 — article — `pre1990`

**Concepts:** Physics (0.89), Astrophysics (0.74), Radiative transfer (0.61), Spectral line (0.57), Absorption (acoustics) (0.53)

**Title:** H I emission-absorption studies with high-velocity resolution

> The properties of interstellar H I are investigated using high-velocity resolution, Arecibo emission-absorption spectra in the direction of 40 radio continuum sources, including 21 at low galactic latitude. This data is compared with previous Arecibo data at intermediate and high galactic latitude to rediscuss some uncertainties in the analysis of H I spectra due to radiative transfer effects, nonzero beamwidth and a nonuniform H I distribution. This comparison corroborates (a) the earlier suggestion that the H I density in the nearest 100 pc is lower than the disk average by about a factor of 2 and (b) the previous separation of H I emission into material associated with absorbing "clouds" and physically independent, not strongly absorbing (INSA) material, each type containing ~50% by mass. A comparison of lines of sight with different geometries supports the previous suggestion that spin temperatures are higher far above the galactic disk. There is little correlation between the properties of the H I emission fluctuations on 3.8' separations and the properties of either the emission or the absorption profiles. Analysis of the high latitude spectra shows that Gaussian fits provide an excellent description of the H I absorption profiles. An observed lack of structure in the absorption profiles with a line width less than 0.5 km s^-1^ indicates that hypothetical cold H I clumps have column densities less than 5 x l0^18^ cm^-2^. From a comparison of H I and OH spectra, it is inferred that the H I in molecular clumps is less than a few percent of the total hydrogen present.

**Verdict:** OK

---

##  97. [W2083252160](https://openalex.org/W2083252160) — 1988 — article — `pre1990`

**Concepts:** Computer science (0.49), Service (business) (0.46), World Wide Web (0.41), Scope (computer science) (0.41), Telecommunications (0.38)

**Title:** Reaching out to the end user with the BIOSIS Connection

> The Biosis Connection was launched on 2 May 1988, as an online search system targeted to research scientists in the life sciences. Since there is no professional society dedicated to serving life scientists as an integrated group, Biosis saw a need to facilitate communications between life scientists by becoming the focal point of information services for this community. Biosis undertook this project well aware of the ‘elusive end user’ phenomenon. Biosis carefully researched ways and means to serve this audience as a first step in achieving the long term goals of the Biosis Connection. The resulting system design and specifications took into account the fact that virtually every successful electronic end user product on the market must appeal to the professional librarian as well. To that end, the Biosis Connection was designed with both a menu‐driven front end package to serve the novice or occasional user in addition to a command language version for the experienced user and/or information professional. The databases included for initial offering were selected to meet current awareness needs or to allow access to databases unavailable on any other online system. None of these compete directly with any other Biosis online database. System enhancements and the development of new databases are ongoing activities, with the first upgrades scheduled for implementation in the fall of 1988. Companion services for document ordering and event referral were incorporated from the start so that the Biosis Connection would be a complete information service. The project scope to start up the Biosis Connection was equivalent to that of establishing a new business. In this paper, the planning, project research and product development processes are examined. The effectiveness of Beta testing the system will also be reviewed. Preliminary market response and formal evaluations received are summarized. Finally, a brief discussion of the highlights and lowlights of building a system like the Biosis Connection is given.

**Verdict:** FLAG: BORDERLINE (I mean it talks about a network so probably OK)

---

##  98. [W1984865131](https://openalex.org/W1984865131) — 1977 — article — `pre1990`

**Concepts:** Globular cluster (0.93), Physics (0.91), Astrophysics (0.59), Ionization (0.54), Hydrogen (0.53)

**Title:** Evidence for ionized hydrogen in the cores of globular clusters

> Photometric and spectrographic observations of 27 globular clusters reveal evidence for the existence of an emission component of H-alpha in the cores of several globular clusters, notably NGC 5824 and the X-ray clusters NGC 1851, 6624, and 7078. UBVR measurements for all 27 clusters show that the colors of the innermost cores (out to about 8 arcsec) are marginally reddened. A time-resolved spectrum of the central 1 by 3 arcsec of the X-ray burst source globular NGC 6624 revealed a remarkable brightening of about 1 magnitude with a duration of approximately 25 min. Concurrent with this apparent flare, H-alpha emission was seen at a radial velocity of -400 km/s relative to the absorption component. Both the emission equivalent width(about 1 A) and variability are consistent with the photometric data.

**Verdict:** OK

---

##  99. [W4298299716](https://openalex.org/W4298299716) — 1984 — article — `pre1990`

**Concepts:** Standardization (0.89), Computer science (0.74), Theme (computing) (0.65), World Wide Web (0.63), Information exchange (0.61)

**Title:** Standardization of implementation format for bibliographic information interchange on magnetic tape

> It may be said that the present age is one wherein computers are being introduced into every possible sphere, even becoming a part of our social lives. The same situation is found in the information community.The value of introducing computers is particularly highly rated as the overall theme of the information community is "Providing needed information to those in need when it is needed." However, due to the evolution of various machine-readable forms of bibliographic information formats, the introduction of computers has, conversely produced an impeding factor when it should have been of service in universal bibliographic control.As is introduced in this script, the Bibliographic Information Exchange Format has been developed as an interface to the various formats. UNIMARC, ISO 2709, UNISIST-Reference Manual, MEKOF, etc., these were proposed together as a multiple number of universal bibliographic information exchange formats.The Common Communication Format, which was to combine the multiple number of universal bibliographic information exchange tape formats, has still not been announced, after 5 and a half years since the problem was raised.Since its establishment, its method of use is not one that would solve the present situation of the various formats now being used, rather it seems that it will be distributed as an option. Moreover, standardization activities are developing in Europe and the U. S. A., leaving many problems to be dealt with in the promotion of bibliographic data exchange.

**Verdict:** FLAG: WRONG_FIELD (although magnetic tape is mentioned this is more about information exchange)

---

## 100. [W1579433101](https://openalex.org/W1579433101) — 1972 — book — `pre1990`

**Concepts:** Debugging (0.72), Computer science (0.71), Computability (0.58), Field (mathematics) (0.56), Subject (documents) (0.51)

**Title:** Mathematical Theory of Computation

> From the Publisher:
Defining his subject as making the art of verifying computer programs (debugging) into a science, the author addresses both practical and theoretical aspects of the process. A self-contained treatment, it includes selected concepts of computability theory and mathematical logic, and each chapter concludes with bibliographic remarks, references, and problems. This book is a classic text on sequential program verification; it has been widely translated from the original Hebrew and is much in demand among graduate students in the field of computer science (it may also be used as an undergraduate text for advanced classes). Unabridged republication of the edition published by McGraw-Hill, New York, 1974. 77 Figures.

**Verdict:** OK

---
