# Phase 1.2 H2 hand audit — sheet

Generated: 100 papers from `section0-sample-1M.parquet`, stratified 50 uniform + 50 pre-1990. Audit seed: `ws2-phase-1.2-h2-audit-seed-v1`.

**Reviewer task:** for each paper below, check:

1. **Field**: is the paper plausibly cs or physics? (if it's primarily another field that just mentions a cs/physics term, FLAG)
2. **Abstract**: is the reconstructed abstract real prose, not garbled / OCR slop / index artifacts?
3. **Pre-1990 junk tokens**: for stratum=pre1990, does the abstract contain post-2000 tokens (e.g., "2024", "GPT", "COVID", "ChatGPT")? FLAG if yes.

Mark each paper with `OK` / `FLAG: <reason>` in the line below the abstract. Pass criterion: **0 FLAGs** out of 100.

---

##   1. [W6905980964](https://openalex.org/W6905980964) — 2023 — dataset — `uniform`

**Concepts:** Download (0.60), Computer science (0.55), Matching (statistics) (0.52), Data mining (0.36), Range (aeronautics) (0.35)

**Title:** Occurrence Download

> A dataset containing 141 species occurrences available in GBIF matching the query: { "TaxonKey" : [ "is Indigofera diversifolia DC." ] } The dataset includes 141 records from 20 constituent datasets; see https://api.gbif.org/v1/occurrence/download/0253098-230224095556074/datasets/export for details. Data from some individual datasets included in this download may be licensed under less restrictive terms.

**Verdict:** _____

---

##   2. [W6924442052](https://openalex.org/W6924442052) — 2021 — dataset — `uniform`

**Concepts:** Download (0.71), Matching (statistics) (0.58), Computer science (0.56), Data mining (0.40), Range (aeronautics) (0.34)

**Title:** Occurrence Download

> A dataset containing 276 species occurrences available in GBIF matching the query: { "and" : [ { "or" : [ "BasisOfRecord is Human Observation", "BasisOfRecord is Specimen", "BasisOfRecord is Fossil" ] }, "HasCoordinate is true", "HasGeospatialIssue is false", "TaxonKey is Macron lividus (A.Adams, 1855)" ] } The dataset includes 276 records from 15 constituent datasets; see https://api.gbif.org/v1/occurrence/download/0065345-210914110416597/datasets/export for details. Data from some individual datasets included in this download may be licensed under less restrictive terms.

**Verdict:** _____

---

##   3. [W6924224121](https://openalex.org/W6924224121) — 2019 — dataset — `uniform`

**Concepts:** Annotation (0.61), Taxon (0.58), Sequence (biology) (0.55), Similarity (geometry) (0.48), Set (abstract data type) (0.47)

**Title:** SH3387655.08FU

> UNITE provides a unified way for delimiting, identifying, communicating, and working with DNA-based Species Hypotheses (SH). All fungal ITS sequences in the international nucleotide sequence databases are clustered to approximately the species level by applying a set of dynamic distance values (<0.5 - 3.0%). All species hypotheses are given a unique, stable name in the form of a DOI, and their taxonomic and ecological annotations are verified through distributed, web-based third-party annotation efforts. SHs are connected to a taxon name and its classification as far as possible (phylum, class, order, etc.) by taking into account identifications for all sequences in the SH. An automatically or manually designated sequence is chosen to represent each such SH. These sequences are released (https://unite.ut.ee/repository.php) for use by the scientific community in, for example, local sequence similarity searches and next-generation sequencing analysis pipelines. The system and the data are updated automatically as the number of public fungal ITS sequences grows.

**Verdict:** _____

---

##   4. [W6916318449](https://openalex.org/W6916318449) — 2024 — dataset — `uniform`

**Concepts:** Measure (data warehouse) (0.51), Physics (0.41), Microwave (0.35), Electron density (0.31), Flow (mathematics) (0.26)

**Title:** LHD MWRM-PXI #75600.2

> Microwave reflectometers measure a density fluctuation, an electron density profile, and a poloidal flow velocity.

**Verdict:** _____

---

##   5. [W2105804376](https://openalex.org/W2105804376) — 1966 — article — `uniform`

**Concepts:** Icon (0.85), Citation (0.72), Download (0.57), Information retrieval (0.49), Computer science (0.48)

**Title:** Heat-Release Profiles in the High-Temperature Oxidation of Acetylene in Shock Waves

> Views Icon Views Article contents Figures & tables Video Audio Supplementary Data Peer Review Share Icon Share Twitter Facebook Reddit LinkedIn Tools Icon Tools Reprints and Permissions Cite Icon Cite Search Site Citation W. C. Gardiner, W. G. Mallard, K. Morinaga, D. L. Ripley, B. F. Walker; Heat‐Release Profiles in the High‐Temperature Oxidation of Acetylene in Shock Waves. J. Chem. Phys. 15 June 1966; 44 (12): 4653–4654. https://doi.org/10.1063/1.1726700 Download citation file: Ris (Zotero) Reference Manager EasyBib Bookends Mendeley Papers EndNote RefWorks BibTex toolbar search Search Dropdown Menu toolbar search search input Search input auto suggest filter your search All ContentAIP Publishing PortfolioThe Journal of Chemical Physics Search Advanced Search |Citation Search

**Verdict:** _____

---

##   6. [W7132538725](https://openalex.org/W7132538725) — 2025 — dissertation — `uniform`

**Concepts:** Physics (0.62), Humanities (0.42), Theology (0.34), Engineering (0.33), Computer science (0.31)

**Title:** Urban Waterfront Revitalization of Grčevo, Integrating 3D Technologies and Sustainable Solutions

> Obale gradova definirane su kao prijelazne zone između urbanog tkiva i vode. One se često smatraju pokretačima urbanog razvoja jer njihovo uređenje ima potencijal stvoriti novu sliku grada, privući investicije i spriječiti propadanje prostora. Ovaj rad predlaže cjelovito uređenje obale na području Grčeva, na potezu od brodogradilišta Viktor Lenac do lučice Borik. Projekt obuhvaća izgradnju suvremene obalne šetnice, uređenje plažnih prostora i formiranje žala, kao i stvaranje uvjeta za smještaj suhe marine (suhe komunalne luke) namijenjene plovilima, čime se prostor obogaćuje dodatnim sadržajima javne i rekreativne namjene. Cilj je revitalizirati sada zapušten i infrastrukturno nedovoljno razvijen dio obale, stvarajući pritom funkcionalan, siguran i krajobrazno privlačan javni prostor. Primarni naglasak stavljen je na projektiranje šetnice, dok su za ostale objekte dane okvirne dimenzije, preliminarna situacija i lokacija izgradnje. Metodološki okvir rada temelji se na primjeni suvremenih tehnologija snimanja i digitalne dokumentacije prostora. Korištenjem LiDAR-a, ručnog LiDAR-a te 3D oblaka točaka, uz primjenu SLAM HLS tehnologije, provodi se precizno trodimenzionalno mapiranje obalnog pojasa. Tako prikupljeni podaci omogućuju detaljnu analizu topografskih, infrastrukturnih i prirodnih elemenata te služe kao podloga za planiranje optimalnih rješenja.

**Verdict:** _____

---

##   7. [W6915254993](https://openalex.org/W6915254993) — 2024 — dataset — `uniform`

**Concepts:** Cyclotron (0.70), Plasma (0.45), Physics (0.42), Range (aeronautics) (0.42), Power (physics) (0.34)

**Title:** LHD ICHPXI #128521.1

> Ion Cyclotron Range of Frequencies (ICRF) heating system to launch fast waves (Ion Cyclotron Range of Frequencies (ICRF) waves) to heat plasma particles by wave-particle interaction. Raw data are forward and reflected power and voltage of transmission lines, 3.5 U/L and 4.5 U/L.

**Verdict:** _____

---

##   8. [W4404619172](https://openalex.org/W4404619172) — 2024 — article — `uniform`

**Concepts:** Gynecology (0.52), Physics (0.44), Philosophy (0.33), Medicine (0.25)

**Title:** ÇİN-JAPONYA İLİŞKİLERİNDE ULUSLARARASI SİSTEM KAYNAKLI DEĞİŞİMLER: TEHDİT DENGESİ TEORİSİ BAĞLAMINDA BİR DEĞERLENDİRME

> Bu çalışma, on dokuzuncu yüzyılın sonlarında belirgin şekilde uluslararası sisteme eklemlenen Japonya ve Çin’in, bu tarihlerden günümüze kadar olan dönemdeki ikili ilişkilerini ve bu ilişkilerin uluslararası sistemin etkisiyle uğradığı değişimleri “Tehdit Dengesi Teorisi” bağlamında açıklamayı amaçlamaktadır. Çalışmada Japonya ve Çin ilişkilerinin tarihi, sistem düzeyinde ve sistem dönemlerine göre değerlendirilmiştir. İki ülkenin on dokuzuncu yüzyılın sonlarından günümüze kadar sırasıyla çok kutuplu, çift kutuplu ve son olarak tek kutuplu veya gevşek tek kutuplu sistemlerdeki ilişkilerinin değişimleri anlatılmış ve bu şekilde dönemsel olarak ortaya çıkan farklılıklar açıklanmaya çalışılmıştır. İki ülke arasında ortaya çıkan bu farklılıkların sebebi realist teori kapsamında Stephen Walt’un öne sürdüğü Tehdit Dengesi Teorisi ile tespit edilmeye çalışılmıştır. Çalışmada, tehdit algılarının değişiminin değerlendirilmesi ve tespiti de Tehdit Dengesi Teorisi kapsamında öne sürülen dört değerlendirme birimine göre yapılmıştır. Bu bağlamda çalışmada ilk olarak, Tehdit Dengesi Teorisi ve değerlendirme birimleri açıklanmıştır. Ardından, günümüze değin Çin-Japonya ilişkileri gözden geçirilmiş ve iki ülke arasındaki temel sorunlar açıklanmıştır. Son olarak, on dokuzuncu yüzyılın sonlarından günümüze kadar geçen sürede meydana gelen sistem değişikliklerinin iki ülke ilişkileri üzerine yansımaları dört değerlendirme birimi temelinde ve tehdit algısı bağlamında değerlendirilmiştir. Varılan sonuca göre, geleneksel rakipler olarak kendileri için birbirlerinden daha büyük tehlikeler hissettikleri dönemlerde Çin ve Japonya daha iyi ilişkilere sahip olmuşlardır. Uluslararası sistemin yapısında kaynaklı olarak kendilerine yönelmiş daha büyük tehditler görmediklerinde ise iki ülke daha sorunlu ve çatışmacı dönemler geçirme başlamışlardır.

**Verdict:** _____

---

##   9. [W6953984462](https://openalex.org/W6953984462) — 2024 — dataset — `uniform`

**Concepts:** Measure (data warehouse) (0.50), Physics (0.41), Field (mathematics) (0.36), Magnetic field (0.36), Materials science (0.25)

**Title:** LHD RAD-9O #175216.1

> Q and V-band (34-74 GHz) ECE ratiometer to measure electron temperature fluctuations in low magnetic field experiments

**Verdict:** _____

---

##  10. [W2291718387](https://openalex.org/W2291718387) — 2015 — article — `uniform`

**Concepts:** Computer vision (0.87), Artificial intelligence (0.85), Computer science (0.76), Mobile robot (0.73), Segmentation (0.70)

**Title:** A fast object segmentation method for mobile robots based on improved depth information

> Due to the rapid development of mobile robots technology, the object recognition is of great practical significance. The real-time performance and robustness of object segmentation in cluttered environments is a considerable problem in robot vision. In this paper, a new object segmentation method using depth information is presented. Firstly, this approach obtains the object candidate region using the depth clue, then accomplished the depth filtering in the object candidate region. Next, the object region is extended to get the better edge information. Finally, the foreground is extracted and the segmentation results is realized on the color image. This method of object segmentation was tested on a real mobile robot platform and the results of experiments confirmed the excellent performance of the proposed method.

**Verdict:** _____

---

##  11. [W2153116986](https://openalex.org/W2153116986) — 1999 — article — `uniform`

**Concepts:** Computer science (0.76), Computer vision (0.63), Artificial intelligence (0.63), Image registration (0.51), Segmentation (0.49)

**Title:** A minimax entropy registration framework for patient setup verification in radiotherapy

> In external beam radiotherapy (EBRT), patient setup verification over the entire course of fractionated treatment is necessary for accurate delivery of a specified dose to the tumor. We are working on the development of a minimax entropy registration framework for patient setup verification using dual portal images and the treatment planning 3D CT dataset. In this paper, we present an overview of our registration framework, where an iteratively and automatically estimated segmentation of the portal image is utilized to more accurately and robustly register the portal image to the 3D treatment-planning CT data. In addition, we describe initial testing of this approach. We note that, due to low resolution and low contrast of the portal images, this registration presents a difficult problem. We also note that the registration of the images in our proposed method is guided by the bony structure visible in the portal and the 3D CT images. However, since the prostate can move with respect to the pelvic bone, we propose using ultrasound images to quantify this movement.

**Verdict:** _____

---

##  12. [W6928783957](https://openalex.org/W6928783957) — 2022 — other — `uniform`

**Concepts:** Overfitting (0.79), Computer science (0.65), Artificial intelligence (0.61), Training set (0.53), Selection (genetic algorithm) (0.52)

**Title:** Por Qué Não Utiliser Alla Språk? Mixed Training with Gradient Optimization in Few-Shot Cross-Lingual Transfer

> The current state-of-the-art for few-shot cross-lingual transfer learning first trains on abundant labeled data in the source language and then fine-tunes with a few examples on the target language, termed target-adapting. Though this has been demonstrated to work on a variety of tasks, in this paper we show some deficiencies of this approach and propose a one-step mixed training method that trains on both source and target data with stochastic gradient surgery, a novel gradient-level optimization. Unlike the previous studies that focus on one language at a time when target-adapting, we use one model to handle all target languages simultaneously to avoid excessively language-specific models. Moreover, we discuss the unreality of utilizing large target development sets for model selection in previous literature. We further show that our method is both development-free for target languages, and is also able to escape from overfitting issues. We conduct a large-scale experiment on 4 diverse NLP tasks across up to 48 languages. Our proposed method achieves state-of-the-art performance on all tasks and outperforms target-adapting by a large margin, especially for languages that are linguistically distant from the source language, e.g., 7.36% F1 absolute gain on average for the NER task, up to 17.60% on Punjabi.

**Verdict:** _____

---

##  13. [W4395159123](https://openalex.org/W4395159123) — 2023 — dataset — `uniform`

**Concepts:** Download (0.77), Computer science (0.41), World Wide Web (0.26)

**Title:** Occurrence Download

> A dataset containing 349 species occurrences available in GBIF matching the query: { "TaxonKey" : [ "is Cephalaria squamiflora (Sieber) Greuter" ] } The dataset includes 349 records from 45 constituent datasets; see https://api.gbif.org/v1/occurrence/download/0017442-230828120925497/datasets/export for details. Data from some individual datasets included in this download may be licensed under less restrictive terms.

**Verdict:** _____

---

##  14. [W6935818570](https://openalex.org/W6935818570) — 2024 — dataset — `uniform`

**Concepts:** Cyclotron (0.56), Physics (0.47), Radiometer (0.45), Electron temperature (0.35), Electron (0.32)

**Title:** LHD RADH #98273.1

> High frequency band, 106-156 GHz, Radiometer (RADH), as an Electron Cyclotron Emission (ECE) measurement for electron temperature profile and fluctuation

**Verdict:** _____

---

##  15. [W6952164338](https://openalex.org/W6952164338) — 2024 — dataset — `uniform`

**Concepts:** Sideband (0.87), Compatible sideband transmission (0.73), Heterodyne (poetry) (0.59), Physics (0.57), Radiometer (0.44)

**Title:** LHD ECE-UFAST #177423.1

> Intermediate frequency signals of 8-O ECE heterodyne radiometer (RADH and RADM) acquired by high speed oscilloscope. Each channel acquires 1) Higher sideband of RADH (Local 132GHz, IF 2-18GHz corresponds to 8-O ECE 132-152 GHz), 2) Lower sideband of RADH (Local 132GHz, IF 2-18 GHz corresponds to 8-O ECE 114-132 GHz), 3) Lower sideband of RADH (Local 132GHz, IF 18-26 GHz corresponds to 8-O ECE 106-114 GHz), and 4) Higher sideband of RADM (Local 95GHz, IF 2-18 GHz corresponds to 8-O ECE 97-113 GHz).

**Verdict:** _____

---

##  16. [W6915355119](https://openalex.org/W6915355119) — 2024 — dataset — `uniform`

**Concepts:** Cyclotron (0.70), Plasma (0.45), Physics (0.42), Range (aeronautics) (0.42), Power (physics) (0.34)

**Title:** LHD ICHPXI #84539.7

> Ion Cyclotron Range of Frequencies (ICRF) heating system to launch fast waves (Ion Cyclotron Range of Frequencies (ICRF) waves) to heat plasma particles by wave-particle interaction. Raw data are forward and reflected power and voltage of transmission lines, 3.5 U/L and 4.5 U/L.

**Verdict:** _____

---

##  17. [W4292771801](https://openalex.org/W4292771801) — 2019 — article — `uniform`

**Concepts:** Pacific islanders (0.77), Educational leadership (0.44), Medical education (0.37), Computer science (0.34), Psychology (0.33)

**Title:** Exploring Culturally Relevant Leadership Development for Pacific Islander American College Students

> Education research focused on Pacific Islanders over the past 30 years has overwhelmingly concluded that U.S. systems of education are failing these students, but the global movement towards culturally relevant and inclusive education has had an indelible impact on the number and types of support available for Pacific Islander students in the continental United States. The purpose of this project is to explore how culturally relevant leadership development shapes the growth and development of Pacific Islander American college students. We examine quantitative and qualitative data from students who are enrolled in a culturally relevant leadership development program for Pacific Islanders in Southern California. We examine how students' identity, relationships, and leadership is related to their identity and histories.

**Verdict:** _____

---

##  18. [W2951302004](https://openalex.org/W2951302004) — 2019 — article — `uniform`

**Concepts:** Process (computing) (0.64), Context (archaeology) (0.62), Computer science (0.59), Driving simulator (0.53), Point (geometry) (0.44)

**Title:** A Game-Based Driving Learning System for Sri Lankan Driving Learners to Enrich the Awareness of Road Rules

> Traffic safety is becoming an important problem in most of the countries. Based on investigations it has been identified that the unawareness of road rules, lack of practice of sudden reactions in hazardous situations are the major causes for accidents. Though there are many driving simulators available, most of them have not addressed the road rules and hazardous incidences that a driver must be aware. Also they are lacking of a proper evaluation of the driving skills and awareness of the driver. Primary objective of the system is to provide a driving learning platform for the learners, trainers as well as evaluators to overcome the existing challenges, which has mainly focused on creating a virtual environment to facilitate the training and testing process in the local context and main areas of violating road rules and regulations by drivers are taken into account. In order to provide a realistic road environment, virtual environments are modeled based on different criteria. Artificial Intelligence techniques like non-player characters and objects, are employed. One of the major components of the simulator is the driver evaluation: a point based method defined upon the rules, road conditions and driving ethics established in the country. Further, the virtual environment provides all the road conditions available, countryside as well as the urban traffic conditions with different weather conditions. The effectiveness of the developed simulator is measured by allowing a selected group of learners to use the simulator for a specific period and assess their driving skills. It can be concluded that training the learners in a virtual environment that similar to the real environment with a proper assessment of their driving skills, awareness of the rules and road signs, and the driving ethics will solve most of the problems we face today.

**Verdict:** _____

---

##  19. [W4251091456](https://openalex.org/W4251091456) — 2019 — article — `uniform`

**Concepts:** Computer science (0.40)

**Title:** Contributors

> Voelcker worked at Spectrum in the late 1980s, at Green Car Reports in the 2010s, and at a dozen media and tech companies in between. In his spare time, he tinkers with old British cars, a retro pursuit he balances with a focus on the future of transportation. The latter interest recently took him to Porsche's R&D center in Weissach, Germany, where he witnessed really fast electricvehicle charging [see "Porsche's Fast-Charge Power Play," p. 30].

**Verdict:** _____

---

##  20. [W3096684918](https://openalex.org/W3096684918) — 2020 — article — `uniform`

**Concepts:** Filter (signal processing) (0.60), Computer science (0.60), Algorithm (0.58), Filter design (0.57), Minification (0.54)

**Title:** Low Complexity FIR Filter Design using Biogeography Optimization Algorithm and its Improved Version

> In this paper, sparse FIR filter design using multiobjective bio geography based optimization is considered. The metaheuristic bio geography based optimization algorithm is inspired by geographical science. It is easier in implementation, robust and faster in convergence. The objective function of filter design includes minimization of pass band ripples and stop band ripples. The tradeoff between the pass band ripple and stop band ripple cannot be solved by a single objective function and therefore a multiobjective optimization problem is formulated to solve the filter design problem. The evaluation of the proposed method is divided into two parts. In the first part, sparse FIR filter designed with the desired filter specification. In the second part, designed sparse FIR filter compared with the existing reporting algorithms. The comparison result shows the proposed method performs better than the existing algorithm and can be used in practical application.

**Verdict:** _____

---

##  21. [W6894388447](https://openalex.org/W6894388447) — 2025 — dataset — `uniform`

**Concepts:** Physics (0.41), Dispersion (optics) (0.40), Wavelength (0.39), Optics (0.34), Plasma (0.28)

**Title:** LHD 133m-vis #167134.1

> Spectral data measured with a high-wavelength dispersion visible spectrometer. Spatial distribution measurements for a poloidal plasma cross section are performed by multiple lines-of-sights. The center wavelength can be changed depending on the purpose of the measurement.

**Verdict:** _____

---

##  22. [W7024659885](https://openalex.org/W7024659885) — 2004 — article — `uniform`

**Concepts:** Theology (0.49), Physics (0.37), Philosophy (0.32), Croatian (0.28), Traditional medicine (0.25)

**Title:** Stoljeće rearanžiranja: nanoznanost i globalno društvo

> Esej "Stoljeće rearanžiranja: nanoznanost i globalno društvo", dovodi u vezu modernu znanost (nanoznanost) i moderno društvo (globalno društvo) kroz odnos nanotehnologizacije i globalizacije kao najvažnijih procesa jedne mreže fenomena koji se dotiču na području tehničkih i društvenih znanosti. Autor karakterizira 21. stoljeće kao stoljeće rearanžiranja u kojem znanost i filozofija funkcioniraju sa zajedničke osnove koja je holistička i pragmatička. Komparacijom novih tehničkih metoda u znanostima o materijalima i novih procesa u društvenoj ontologiji autor stavlja u odnos dva pristupa i dvije skale identifikacije i reprezentacije: nanoskalu na području zananosti ο materijalima i globalnu skalu na području znanosti ο društvenim odnosima. Tehničke znanosti u formi nanoznanosti orijentirane su na stvaranje nove infrastrukturne paradigme: "ambijenta inteligentnog prostora" vođenog idejom "svi-u-digitalnom-svijetu". Društvene znanosti, koje sudjeluju na planu integracije i globalizacije, orijentirane su na stvaranje nove transnacionalne i spekulativne paradigme: "mobilnog hiper-prostora za internacionalno poslovanje" vođene idejom "svi-u-demokratskom-svijetu". Obje vrste znanosti proizvode istu vrstu nevidljive ontologije koja je dostupna samo virtualnoj identifikaciji i reprezentaciji zasnovanoj na osmišljavanju, stvaranju i proizvodnji programibilne supstancije i programibilnog identiteta. One produciraju identičnost / uniformnost u funkcionalnom operiranju tehničkim sredstvima i političkim principima. U sintagmi "društvo zasnovano na znanju" termin "znanje" ima značenje "znanje proizvodnje, znanje upotrebe i znanje operiranja pametnim (programibilnim) materijalima i pametnim (programibilnim) identitetom". U "D&D svijetu" (digitalnom & demokratskom svijetu) svi ljudi moraju znati upotrebljavati tehnološki mikro-svijet i politički makro-svijet kako bi postigli isti cilj: kontrolu nad prirodom i društvom. Nevidljivost ili iščezavanje realnih stvari, realnih sredstava komunikacije i realnih društvenih odnosa, jeste novo tehničko i ideološko sredstvo stvaranja "novog čarobnog svijeta".

**Verdict:** _____

---

##  23. [W7141945970](https://openalex.org/W7141945970) — 2026 — preprint — `uniform`

**Concepts:** Physics (0.61), Electromagnetic shielding (0.46), Multiplet (0.45), Nonlinear system (0.41), Dark energy (0.38)

**Title:** Chronowaves as a New Communication Channel

> Abstract This paper provides a theoretical and engineering framework for a novel communication channel based on the temporal multiplet (field φ) within the Temporal Theory of the Universe (TTU). Addressing the fundamental limits of the electromagnetic paradigm — spectral congestion and EMI shielding — we propose a transition to Layer 0: the spacetime substrate. The information carrier is defined as a scalar chronowave, a longitudinal perturbation of time density. We analyze the pre-cursor effect, where substrate phase-state shifts precede the inertial response of matter, creating an informational lead time. The proposed architecture utilizes geometric signal amplification (Kozyrev focus) and a multi-tier detection stack (quantum, mechanical, and resonant). We formalize the "Dark Channel" protocol (CW-PSK, Kiev Correlation Protocol), ensuring signal permeability through plasma and metallic barriers. Historical anomalies (EM Drive, superconductivity) are unified under a predicted 0.45 MHz universal resonance, transitioning astronomical observation from passive retrospection to an operational present. Keywords: Chronowave, Layer 0, TTU/TTG, pre-cursor effect, 0.45 MHz resonance, scalar perturbation, disformal coupling, "Dark Channel", operational present. TABLE OF CONTENTS 1. Introduction: Crisis of the Energy Paradigm 1.1. Maxwell's Limits: "Spectral Hunger" and the Energy Dead End 1.2. The Shielding Problem: Where Light is Powerless 1.3. Paradigm Shift: From Photons to Substrate Structure 2. Physics of the Carrier: The Temporal Multiplet and the φ Field 2.1. The φᵃ Substrate: The Fundamental "Data Bus" of the Universe 2.2. Disformal Coupling: Logarithmic Potential and Nonlinearity 2.3. Chronowave as a Scalar: Longitudinal Perturbations vs. EM Waves 3. The Precursor Effect: Informational Lead Time (v ≈ c) 3.1. Event Separation: Phase vs. Inertia 3.2. Lead Time Calculation (Δt): The Accumulated Lag Formula 3.3. Causality Compliance: Why This Is Not FTL 4. Geometric Amplification: The Kozyrev Focus 4.1. The Mirror as a Lens for Time: Compressing the Structure 4.2. The Local Differential Principle: The "Knife" Cutting Through Time 4.3. Gain Coefficient (G_geo): Paraboloid Geometry 5. The Tiered Hardware Stack: Detection Methods 5.1. Quantum Detector (Casimir Effect): Vacuum Pressure 5.2. Macro-Mechanical Sensor (Torsion Balance): Temporal Wind 5.3. Resonant Transducer: Tungsten and Quartz 5.4. Differential Bridge (Wheatstone–Kozyrev) 6. Layer 0 Protocol: Encoding and Super-Permeability 6.1. Phase Modulation (CW-PSK): Digital Signal in Temporal Potential 6.2. Kiev Correlation Protocol: Clarity from Noise 6.3. Engineering the "Dark Channel": Through Plasma and Steel 7. Conclusion: A New Era of Temporal Monitoring 7.1. Summary: The Superiority of the "Dark Channel" 7.2. Falsifiability of the Theory: Experimental Trigger 7.3. Operational Present: From Observer to Actor Appendix A. Historical Context and Unification of Anomalous Phenomena Within the Temporal Theory of the Universe (TTU)

**Verdict:** _____

---

##  24. [W7131654004](https://openalex.org/W7131654004) — 2026 — dataset — `uniform`

**Concepts:** Download (0.66), Computer science (0.58), Matching (statistics) (0.54), Data mining (0.39), Range (aeronautics) (0.36)

**Title:** Occurrence Download

> A dataset containing 31389 species occurrences available in GBIF matching the query: { "or" : [ "Geometry POLYGON((-44.46681 8.26391,-47.35369 2.91241,-40.41914 1.55933,-44.46681 8.26391))", "Geometry POLYGON((-74.05968 4.63754,-74.05923 4.63494,-74.05745 4.63474,-74.05496 4.6374,-74.05613 4.64127,-74.05712 4.64135,-74.05864 4.63952,-74.05968 4.63754))" ] } The dataset includes 31389 records from 88 constituent datasets; see https://api.gbif.org/v1/occurrence/download/0000223-260226173443078/datasets/export for details. Data from some individual datasets included in this download may be licensed under less restrictive terms.

**Verdict:** _____

---

##  25. [W6967989941](https://openalex.org/W6967989941) — 2024 — article — `uniform`

**Concepts:** Knowledge management (0.46), Data management (0.45), Process management (0.41), Computer science (0.39), Work (physics) (0.34)

**Title:** Annex 3 Communication and Data Management Guidelines for CoARA Working Groups

> Communication and Data Management Guidelines for CoARA WGs. The current version is under community review by CoARA WG Co-chairs.

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

##  28. [W2039744893](https://openalex.org/W2039744893) — 2010 — article — `uniform`

**Concepts:** Jamming (0.85), Frequency-shift keying (0.81), Additive white Gaussian noise (0.80), Fading (0.66), Nakagami distribution (0.55)

**Title:** Performance analysis of FFH/MFSK receivers with noise‐normalisation combining over Nakagami‐<i>m</i>fading channels with partial‐band jamming

> Abstract The performance of a fast frequency‐hopped M ‐ary orthogonal frequency‐shift‐keying (FFH/MFSK) receiver with noise‐normalisation combining over Nakagami‐ m fading channels with partial‐band noise jamming and additive white Gaussian noise (AWGN) is analysed. Instead of numerical integration, a closed‐form error probability expression is obtained. The analytical results validate the simulation results. It is shown that there is an optimum diversity order and the corresponding best‐case performance is investigated. Copyright © 2010 John Wiley &amp; Sons, Ltd.

**Verdict:** _____

---

##  29. [W4414345173](https://openalex.org/W4414345173) — 2025 — article — `uniform`

**Concepts:** Quantum entanglement (0.85), Physics (0.72), Quantum mechanics (0.57), Statistical physics (0.54), Quantum (0.54)

**Title:** Quantum Information Perspective on Many-Body Dispersive Forces

> Despite its ubiquity, the quantum many-body properties of dispersion remain poorly understood. Here, we investigate the entanglement distribution in assemblies of quantum Drude oscillators, minimal models for dispersion-bound systems. We establish an analytic relationship between entanglement and correlation energy and show how entanglement monogamy determines whether many-body corrections to the pair potential are attractive, repulsive, or zero. These findings, demonstrated in trimers and extended lattices, apply in more general chemical environments where dispersion coexists with other cohesive forces.

**Verdict:** _____

---

##  30. [W7099199220](https://openalex.org/W7099199220) — 2009 — article — `uniform`

**Concepts:** Clutter (0.77), Point target (0.67), Algorithm (0.63), Track-before-detect (0.60), Robustness (evolution) (0.59)

**Title:** Particle Filter Based Algorithm for StateEstimation of Dim Moving Point Targets in

> Abstract—Under the condition of the targets ’ initial information is already estimated successfully, This paper presents a real-time target tracking method based on particle filter (PF) update algorithm. According to the particles &amp;apos; transmission characteristics and the measurements from a single frame detection, the algorithm estimate a target’s following moving state. In this way, the dim moving point target could be tracked successfully under the low signal-noise-ratio (SNR) in IR image sequence. But it comes to the multiple targets ’ tracking; we should take the data integration into account. In order to reduce the amount of calculation, we use the data fusion method to divide the measurements in the overlapped parts of windows, appoints the measurements for the corresponding target. That is the Nearest Neighbor Standard Filter (NNSF) theory is used to choose the target for a measurement. The paper introduced the related theory and the concrete steps for accomplish the algorithm and also simulated the proposed tracking algorithm on the MATLAB platform. Experimental analysis and results showed that the algorithm achieved real-time, dynamic stability and robustness while track the random moving targets in high clutter environment. Index Terms—particle filter, single frame detection, measurement division, state estimation, image sequence I.

**Verdict:** _____

---

##  31. [W2603876198](https://openalex.org/W2603876198) — 2016 — article — `uniform`

**Concepts:** Task (project management) (0.69), Object (grammar) (0.57), Physical medicine and rehabilitation (0.54), Computer science (0.47), Artificial intelligence (0.33)

**Title:** Credit Assignment across Limbs in a Bimanual Object Lifting Task (P4.063)

> Objective: To examine credit assignment during a natural object lifting task. Background: Despite our generally skilled interactions with the environment, the motor system invariably makes mistakes. For example, we may lift an object only to find that it is heavier than predicted. To learn from our mistakes, the cause of the error has to be identified by the motor system, a process termed credit assignment. The present study examined whether small errors in lifting forces generalized across limbs as a test of whether they are attributed to the self as opposed to the external environment. If the errors in lifting are attributed to the self, the accumulation of error should remain with the hand performing the lift. Methods: Twenty-nine students completed a bimanual object lifting task. The participant’s left hand always lifted the same block, whereas the right hand lifted a block that gradually increased in weight every ten trials. Following eighty lifts in which the weight in one hand gradually increased, the participant lifted a set of new blocks using a crossed-arm lifting style (lifting the block on the left with the right hand). The initial peak in load force rate (PkLFR) and the load force at the peak load force rate (LF@PkLFR), measures known to be sensitive to a participant’s weight prediction, were examined. Results: PkLFR and LF@PkLFR increased in the right hand between the first and last trial, indicating participants accommodated the change in object weight. However, during the crossed-arm object lifting trials, no differences between the hands were observed. Conclusions: This research suggests small errors in motor control are not always attributed to the self, and may at times be attributed to the external environment. By learning how error-based learning is accomplished, we can create better artificial limbs and more thoroughly assess motor impairments.

**Verdict:** _____

---

##  32. [W6952131437](https://openalex.org/W6952131437) — 2025 — dataset — `uniform`

**Concepts:** Extreme ultraviolet (0.55), Spectroscopy (0.52), Divertor (0.47), Measure (data warehouse) (0.46), Atomic physics (0.43)

**Title:** LHD EUVLong2 #168201.1

> Extreme ultraviolet (EUV) and vacuum ultraviolet (VUV) spectroscopy diagnostics are applied to measure wavelength spectra including line emissions released from Ne ions ranging from low to high charge states simultaneously in a single discharge of the Ne-seeded divertor heat load reduction experiments in LHD.

**Verdict:** _____

---

##  33. [W2035540682](https://openalex.org/W2035540682) — 1995 — article — `uniform`

**Concepts:** Citation (0.72), Altmetrics (0.67), Icon (0.63), Computer science (0.45), World Wide Web (0.28)

**Title:** Bond Strength Trends in Halogenated Methanols: Evidence for Negative Hyperconjugation?

> ADVERTISEMENT RETURN TO ISSUEPREVArticleNEXTBond Strength Trends in Halogenated Methanols: Evidence for Negative Hyperconjugation?William F. Schneider, Barbara I. Nance, and Timothy J. WallingtonCite this: J. Am. Chem. Soc. 1995, 117, 1, 478–485Publication Date (Print):January 1, 1995Publication History Published online1 May 2002Published inissue 1 January 1995https://pubs.acs.org/doi/10.1021/ja00106a055https://doi.org/10.1021/ja00106a055research-articleACS PublicationsRequest reuse permissionsArticle Views286Altmetric-Citations53LEARN ABOUT THESE METRICSArticle Views are the COUNTER-compliant sum of full text article downloads since November 2008 (both PDF and HTML) across all institutions and individuals. These metrics are regularly updated to reflect usage leading up to the last few days.Citations are the number of other articles citing this article, calculated by Crossref and updated daily. Find more information about Crossref citation counts.The Altmetric Attention Score is a quantitative measure of the attention that a research article has received online. Clicking on the donut icon will load a page at altmetric.com with additional details about the score and the social media presence for the given article. Find more information on the Altmetric Attention Score and how the score is calculated. Share Add toView InAdd Full Text with ReferenceAdd Description ExportRISCitationCitation and abstractCitation and referencesMore Options Share onFacebookTwitterWechatLinked InRedditEmail Other access optionsGet e-Alertsclose Get e-Alerts

**Verdict:** _____

---

##  34. [W6961773619](https://openalex.org/W6961773619) — 2021 — dataset — `uniform`

**Concepts:** Annotation (0.61), Taxon (0.58), Sequence (biology) (0.55), Similarity (geometry) (0.48), Set (abstract data type) (0.47)

**Title:** SH1737664.08FU

> UNITE provides a unified way for delimiting, identifying, communicating, and working with DNA-based Species Hypotheses (SH). All fungal ITS sequences in the international nucleotide sequence databases are clustered to approximately the species level by applying a set of dynamic distance values (<0.5 - 3.0%). All species hypotheses are given a unique, stable name in the form of a DOI, and their taxonomic and ecological annotations are verified through distributed, web-based third-party annotation efforts. SHs are connected to a taxon name and its classification as far as possible (phylum, class, order, etc.) by taking into account identifications for all sequences in the SH. An automatically or manually designated sequence is chosen to represent each such SH. These sequences are released (https://unite.ut.ee/repository.php) for use by the scientific community in, for example, local sequence similarity searches and next-generation sequencing analysis pipelines. The system and the data are updated automatically as the number of public fungal ITS sequences grows.

**Verdict:** _____

---

##  35. [W2804252553](https://openalex.org/W2804252553) — 2018 — article — `uniform`

**Concepts:** Computer science (0.68), Reliability (semiconductor) (0.67), Demand response (0.61), Reliability engineering (0.55), Renewable energy (0.53)

**Title:** i13DR

> With the ongoing integration of Renewable Energy Sources (RES), the complexity of power grids is increasing. Due to the fluctuating nature of RES, ensuring the reliability of power grids can be challenging. One possible approach for addressing these challenges is Demand Response (DR) which is described as matching the demand for electrical energy according to the changes and the availability of supply. However, implementing a DR system to monitor and control a broad set of electrical appliances in real-time introduces several new complications including ensuring reliability and financial feasibility of the system. In this work, we address these issues by designing and implementing a distributed real-time DR infrastructure for laptops, which estimates and controls the power consumption of a network of connected laptops in response to the fast irregular changes of RES. The result of our field experiments confirms that our system successfully schedules and executes rapid and effective DR events. However, the accuracy of estimated power consumption of all participating laptops is relatively low, directly caused by our software-based approach.

**Verdict:** _____

---

##  36. [W6886977180](https://openalex.org/W6886977180) — 2024 — dataset — `uniform`

**Concepts:** Download (0.67), Matching (statistics) (0.58), Computer science (0.56), Range (aeronautics) (0.45), Data mining (0.34)

**Title:** Occurrence Download

> A dataset containing 8662 species occurrences available in GBIF matching the query: { "and" : [ "TaxonKey is Pelobates cultripes (Cuvier, 1829)", "HasCoordinate is true", "Year is greater than or equal to 2011", "Year is less than or equal to 2024" ] } The dataset includes 8662 records from 129 constituent datasets; see https://api.gbif.org/v1/occurrence/download/0010642-240506114902167/datasets/export for details. Data from some individual datasets included in this download may be licensed under less restrictive terms.

**Verdict:** _____

---

##  37. [W7111010977](https://openalex.org/W7111010977) — 2025 — article — `uniform`

**Concepts:** Materials science (0.65), Photonics (0.60), Transistor (0.52), Optoelectronics (0.50), Broadband (0.49)

**Title:** Organic PhotonicSynapses with UV–Vis–NIRBroadband Perception Based on Organic Electrochemical Transistors

> Organic photonic synaptic devices have shown immense potential for emulating the visual perception function of the human retina. In particular, organic electrochemical transistors (OECTs) with photoresponse ability are considered promising choices because of their advantages in low-voltage operation, mechanical flexibility, and biocompatibility. However, current research is limited, and deeper investigations into the materials, devices, and their perception capability are needed. Herein, we introduce a solid-state organic electrochemical transistor based on an organic bulk heterojunction film, which exhibits a broadband response from ultraviolet to near-infrared (365–850 nm) and can simulate fundamental biological synaptic behaviors across multiple wavelengths. Moreover, the device can emulate the learning, forgetting, and relearning processes, as well as the image recognition and memory functions. By employing a trichromatic perception simulation based on convolutional operations, the device successfully achieves image preprocessing capabilities, demonstrating the promising potential of our OECT-based photonic synapses in artificial visual perception systems.

**Verdict:** _____

---

##  38. [W4242183320](https://openalex.org/W4242183320) — 1988 — article — `uniform`

**Concepts:** Computer science (0.31)

**Title:** AAAS-African Programs Under Way

> Article MetricsDownloadsCitationsNo data available.012AugSepOctNovDecJan810Total6 Months12 MonthsTotal number of downloads for the most recent 6 whole calendar months.

**Verdict:** _____

---

##  39. [W7141371211](https://openalex.org/W7141371211) — 2026 — dataset — `uniform`

**Concepts:** Amplitude (0.46), Bandwidth (computing) (0.43), Physics (0.40), Sampling (signal processing) (0.39), High resolution (0.26)

**Title:** LHD fmp_amp #178543.1 (analyzed)

> Time evolution of magnetic fluctuation amplitude with high time resolution obtained in certain bandwidth (100 kHz sampling rate).

**Verdict:** _____

---

##  40. [W6958860007](https://openalex.org/W6958860007) — 2016 — other — `uniform`

**Concepts:** Holography (0.82), Realization (probability) (0.74), Computer vision (0.69), Computer science (0.66), Computer graphics (images) (0.62)

**Title:** Realization of real-time interactive 3D image holographic display [Invited]

> Realization of a 3D image holographic display supporting real-time interaction requires fast actions in data uploading, hologram calculation, and image projection. These three key elements will be reviewed and discussed, while algorithms of rapid hologram calculation will be presented with the corresponding results. Our vision of interactive holographic 3D displays will be discussed.

**Verdict:** _____

---

##  41. [W4322731357](https://openalex.org/W4322731357) — 2020 — book-chapter — `uniform`

**Concepts:** Surprise (0.87), Backcasting (0.69), Futures contract (0.68), Curriculum (0.61), Key (lock) (0.60)

**Title:** Key Messages

> We are facing unprecedented challenges – social, economic and environmental – driven by accelerating globalisation and a faster rate of technological developments. At the same time, those forces are providing us with myriad new opportunities for human advancement. The future is uncertain and futures often surprise us; but we need to be open and ready for it and we can also surprise our future. Some strategies include: 1) forecasting future needs of society and actively taking into account the students' needs, interests and voices when designing curriculum, and 2) backcasting, i.e. articulating a shared vision for student profiles as desired student outcomes, then looking back to today to identify curriculum changes necessary to achieve the shared vision.

**Verdict:** _____

---

##  42. [W2378887358](https://openalex.org/W2378887358) — 2013 — article — `uniform`

**Concepts:** Generality (0.75), Test (biology) (0.65), Computer science (0.54), Process (computing) (0.50), Test data (0.45)

**Title:** The Generality and Analysis of Engine Performance Test

> This paper has generally discussed some problems during engine performance test and makes some summarizations about data analysis and equipment of engine performance test combined with actual situations.Summarized in this paper about how to complete the engine performance experiment effectively,and induced how to solve the test problems that you may encounter in the process of experiment.

**Verdict:** _____

---

##  43. [W7014994288](https://openalex.org/W7014994288) — 2000 — article — `uniform`

**Concepts:** Underwater acoustic communication (0.73), Underwater (0.70), Acoustics (0.58), Underwater acoustics (0.52), Computer science (0.51)

**Title:** The ROBLINKS underwater acoustic communication experiments:

> Within the EU-MAST III project ROBLINKS waveforms and algorithms have been developed to establish robust underwater acoustic communication links with high data rates Ã­n shallow water. To evaluate the signalling schemes a wide range of experiments has been performed during a sea trial that has been held in May 1999 in the North Sea, off rhe Dutch coast. The resulting data set consists of recordings of the newly developed waveforms, of more conventional communication signals for comparison, and of signals to probe the acoustic channel. Environmental data have also been collected to analyze and understand the propagation conditions during the transmissions. The most interesting and illustrative part of the data set will be made available for further analysis after the end of the ROBLINKS project

**Verdict:** _____

---

##  44. [W6953292706](https://openalex.org/W6953292706) — 2024 — dataset — `uniform`

**Concepts:** Rogowski coil (0.78), Magnetohydrodynamic drive (0.70), Physics (0.56), Magnetic field (0.51), Large Helical Device (0.48)

**Title:** LHD Magnetics_C #190126.1

> Magnetic measurements for estimating global parameters and for magnetohydrodynamic (MHD) study to introduce diamagnetic flux measurement and MHD mode analysis. Various types of magnetic sensors are used; Rogowski coils and magnetic probes inside and ourside the LHD vacuum vessel.

**Verdict:** _____

---

##  45. [W2754810232](https://openalex.org/W2754810232) — 2017 — article — `uniform`

**Concepts:** Exponential stability (0.82), Artificial neural network (0.60), Exponential function (0.55), Control theory (sociology) (0.54), Mathematics (0.54)

**Title:** Almost sure exponential stability of stochastic Cohen-Grossberg neural networks with Markovian jumping and impulses

> By employing the Lyapunov function method and average impulsive interval approach, the almost sure exponential stability for stochastic Cohen-Grossberg neural networks with Markovian jumping and impulses are considered. A set of sufficient conditions of almost sure exponential stability are derived. An example is given to illustrate the effectiveness of the results obtained.

**Verdict:** _____

---

##  46. [W2007040212](https://openalex.org/W2007040212) — 2010 — article — `uniform`

**Concepts:** Physics (0.58), Molecular biology (0.35), Biology (0.16)

**Title:** CITOLOGIA DE LAVADO BRONCOALVEOLAR DE CÃES: COMPARAÇÃO ENTRE LÂMINAS A FRESCO E CONSERVADAS EM FORMOL

> O lavado broncoalveolar em cães é um método diagnóstico recomendado em casos de enfermidades do trato respiratório inferior, quando exames de rotina não permitem um diagnóstico conclusivo. O exame baseia-se na análise citológica e confecção de lâminas com o material a fresco, ou seja, logo após a coleta, o que pode inviabilizar a técnica em casos de difícil acesso aos laboratórios especializados. Para isso, faz-se necessário um meio de conservação das amostras, aumentando o tempo de vida útil do material a ser analisado. Assim, realizou-se o lavado broncoalveolar em quatorze cães adultos saudáveis. As amostras foram separadas em duas alíquotas: a primeira confeccionada a fresco por sedimentação em câmara de Suta, e a segunda processada uma semana depois, com a amostra conservada em formol. As lâminas foram coradas pelo corante rápido Panótico. Avaliou-se o volume infundido e o volume recuperado, o aspecto macroscópico, a contagem de células nucleadas, a análise diferencial de células e a análise descritiva das lâminas quanto à celularidade, presença de muco, hemácias, leucócitos e células, íntegras ou degeneradas. A análise estatística foi realizada com teste t, para amostras pareadas com p&lt;0,05. Foram encontrados aumento significativo na quantidade de linfócitos e diminuição do número de macrófagos nas amostras conservadas em formol. As demais observações foram similares em ambos os grupos. Portanto, a conservação do material do lavado broncoalveolar de cão em formol, durante uma semana, preservou as células, tornando viável a técnica do lavado broncoalveolar.

**Verdict:** _____

---

##  47. [W6934804956](https://openalex.org/W6934804956) — 2024 — dataset — `uniform`

**Concepts:** Rogowski coil (0.78), Magnetohydrodynamic drive (0.70), Physics (0.56), Magnetic field (0.51), Large Helical Device (0.48)

**Title:** LHD Magnetics_E #156745.1

> Magnetic measurements for estimating global parameters and for magnetohydrodynamic (MHD) study to introduce diamagnetic flux measurement and MHD mode analysis. Various types of magnetic sensors are used; Rogowski coils and magnetic probes inside and ourside the LHD vacuum vessel.

**Verdict:** _____

---

##  48. [W7031030651](https://openalex.org/W7031030651) — None — other — `uniform`

**Concepts:** George (robot) (0.66), Computer science (0.45), Matrix (chemical analysis) (0.38), Engineering (0.34), Computer graphics (images) (0.30)

**Title:** WHY LIVE A LIE?

> Performer: IRVING KAUFMAN; The Ambassadors Writer: GILBERT; KOEHLER Ballad; Accompaniment by. Digitized at 78 revolutions per minute. Four stylii were used to transfer this record. They are 3.5mil truncated eliptical, 2.3mil truncated conical, 2.8mil truncated conical, 3.3mil truncated conical. These were recorded flat and then also equalized with Turnover: 500.0. The preferred versions suggested by an audio engineer at George Blood, L.P. have been copied to have the more friendly filenames. Matrix number: A14856 Catalog number: A 14856

**Verdict:** _____

---

##  49. [W2963807684](https://openalex.org/W2963807684) — 2019 — article — `uniform`

**Concepts:** Cosmic ray (0.89), Physics (0.84), Neutrino (0.80), Observatory (0.76), Neutrino detector (0.62)

**Title:** Cosmic ray composition study using machine learning at the IceCube Neutrino Observatory

> The evaluation of mass composition of cosmic rays in the knee region (~3 PeV) is critical to understanding the transition in the origin of cosmic rays from galactic to extragalactic sources. The IceCube Neutrino Observatory at the South Pole is a multi-component detector consisting of the surface IceTop array and the deep in-ice IceCube detector. By applying modern machine-learning techniques to cosmic-ray air showers reconstructed coincidentally in both detector components of IceCube observatory, the energy and the mass of primary cosmic rays in this transition region can be measured. In this contribution, we will discuss the reconstruction performance and composition sensitivity of IceCube observables presently under development.

**Verdict:** _____

---

##  50. [W1496376740](https://openalex.org/W1496376740) — 2012 — article — `uniform`

**Concepts:** Interfacing (0.90), Electromyography (0.71), Interface (matter) (0.71), Physical medicine and rehabilitation (0.60), Exoskeleton (0.56)

**Title:** Review of EMG-based neuromuscular modeling for the use of upper limb control

> Assistive robots have made great contributions to disabled people in physiotherapy and rehabilitation areas. The interface between patients and medical devices plays a significant role for patients to operate these kinds of robots. This review introduces the current research and development of neuromuscular interfaces, especially the new research directions with special focus on modeling of musculoskeletal systems for interfacing purposes. The paper also summarises the function and prominent advantage of using surface Electromyography (sEMG) signals for the interface. The elbow joint was used as an example to go through the working steps of both human biological systems and neuromuscular interfaces. Further developments were also discussed to improve the interface to meet medical demands.

**Verdict:** _____

---

##  51. [W7031318144](https://openalex.org/W7031318144) — 1959 — other — `pre1990`

**Concepts:** Theme (computing) (0.56), Engineering (0.35), Suite (0.34), Computer science (0.32), Waltz (0.32)

**Title:** Reeds in Hi-Fi

> Comprend : Igor beaver - If you could see me now - Yardbird suite - Impressionism - Walking shoes - Theme for alto - Our waltz - Spring is here - Polytonal blues - Collaboration - Interlude

**Verdict:** _____

---

##  52. [W2327918537](https://openalex.org/W2327918537) — 1937 — article — `pre1990`

**Concepts:** Content (measure theory) (0.56), Link (geometry) (0.45), Computer science (0.44), Information retrieval (0.36), Mathematics (0.33)

**Title:** S. C. Kleene. λ-definability and recursiveness. Duke mathematical journal, Bd. 2 (1936), S. 340–353.

> An abstract is not available for this content so a preview has been provided. Please use the Get access link above for information on how to access this content.

**Verdict:** _____

---

##  53. [W7007924918](https://openalex.org/W7007924918) — 1803 — other — `pre1990`

**Concepts:** The Internet (0.55), Upload (0.45), Art (0.40), Computer science (0.33), World Wide Web (0.32)

**Title:** Apollodori Atheniensis Bibliothecae Libri Tres Et Fragmenta

> Book digitized by Google from the library of Oxford University and uploaded to the Internet Archive by user tpb.

**Verdict:** _____

---

##  54. [W2331191781](https://openalex.org/W2331191781) — 1989 — article — `pre1990`

**Concepts:** Ion (0.63), Hydrogen (0.63), Molecule (0.59), Hydrogen molecule (0.51), Atomic physics (0.47)

**Title:** Partial Wave Analysis of Hydrogen Molecule Ion

> A nonadiabatic procedure is proposed to obtain the eigensolutions of the hydrogen molecule ion. The partial wave behavior of the electron and the proton pair in the three lowest states is investigated in detail in this paper. The overlap of nodes for different partial waves of the protons is found.

**Verdict:** _____

---

##  55. [W2159221511](https://openalex.org/W2159221511) — 1986 — article — `pre1990`

**Concepts:** Calibration (0.68), Characterization (materials science) (0.67), Dosimetry (0.64), Physics (0.55), Ionization (0.47)

**Title:** Techniques Of Absolute Low Energy X-Ray Calibration

> Recent advances in pulsed plasma research, materials science, and astrophysics have required many new diagnostic instruments for use in the low energy x-ray regime. The characterization of these instruments has provided a challenge to instrument designers and provided the momentum to improve x-ray sources and dosimetry techniques. In this paper, the present state-of-the-art in low energy x-ray characterization techniques is reviewed. A summary is given of low energy x-ray generator technology and dosimetry techniques including a discussion of thin window proportional counters and ionization chambers. A review is included of the widely used x-ray data bases and a sample of ultra-soft x-ray measuring techniques is discussed. These techniques include sub-femtoampere current measuring procedures, chopped x-ray source generators, phase sensitive detection of ultralow currents, and angular divergence measurements.

**Verdict:** _____

---

##  56. [W2028760745](https://openalex.org/W2028760745) — 1981 — article — `pre1990`

**Concepts:** Cyclotron (0.81), Physics (0.69), Atomic physics (0.66), Ion (0.61), Electron (0.51)

**Title:** The relationship of field‐aligned currents to electrostatic ion cyclotron waves

> Two sources of free energy for driving ion cyclotron waves have been observed on the S3‐3 satellite: field‐aligned currents and ion beams. Since the waves are destabilized by the thermal electron drift and not the current, before correlating observations of field‐aligned currents with ion cyclotron waves, it is first necessary to determine that the current is primarily carried by thermal electrons. Comparisons of the current carried by energetic particles with the current measured by the magnetometer during several events shows that this is sometimes the case. Statistical studies indicate that the field‐aligned current density is correlated with the spectral density during ion cyclotron events. The combination of the results of this report and those of Kintner et al. (1979) is consistent with the hypothesis that the observed ion cyclotron waves are driven by a combination of ion beams and electron drift. However, the available data set does not unambiguously identify the free energy source.

**Verdict:** _____

---

##  57. [W238155183](https://openalex.org/W238155183) — 1981 — article — `pre1990`

**Concepts:** Safety stock (0.82), Inventory investment (0.59), Operations research (0.54), Stock (firearms) (0.53), Economic order quantity (0.51)

**Title:** Relating Expected Inventory Backorders to Safety Stock Investment Levels.

> The objective of this research was to develop a method to define and predict the relationship between inventory performance and safety stock investment for the Defense Electronics Supply Center (DESC) inventory. DESC uses the model prescribed by DoD Instruction 4140.39 to set individual item safety stock levels. This model minimizes the sum of the variable order and holding costs subject to a constraint on the expected inventory perofmrance as measured by the number of time-weighted essentiality-weighted requisitions short (backorders). An important consideration in selecting the constraint for this model is the safety stock investment required for various levels of performance. This thesis uses multi-variate regression analysis and forecasting techniques to predict the relationship between expected performance and required investment. The author concludes that this method produces accurate predictions of the relationship. The recommended model produced average absolute errors of about three percent when tested against historical data from the DESC inventory. (Author)

**Verdict:** _____

---

##  58. [W7001947868](https://openalex.org/W7001947868) — 1953 — other — `pre1990`

**Concepts:** George (robot) (0.45), Mathematics (0.35), Art (0.33), Computer science (0.32), Matrix (chemical analysis) (0.29)

**Title:** LULLABY OF BIRDLAND

> Performer: ERROLL GARNER; Wyatt Ruther; "Fats" Heard Writer: G. Shearing (piano); (bass); (drums). Digitized at 78 revolutions per minute. Four stylii were used to transfer this record. They are 3.5mil truncated eliptical, 2.3mil truncated conical, 2.8mil truncated conical, 3.3mil truncated conical. These were recorded flat and then also equalized with Turnover: 400.0, Rolloff: -12.0. The preferred versions suggested by an audio engineer at George Blood, L.P. have been copied to have the more friendly filenames. Matrix number: AA 21117.1H Catalog number: B 21117 H

**Verdict:** _____

---

##  59. [W79240188](https://openalex.org/W79240188) — 1981 — article — `pre1990`

**Concepts:** Noise barrier (0.91), Roadway noise (0.65), Transport engineering (0.61), Noise (video) (0.58), Engineering (0.47)

**Title:** HIGHWAY NOISE BARRIERS

> This summary of progress on highway noise barriers gives quantitative and qualitative perspectives of the design, construction, maintenance, and impacts of the barriers that have been built to mitigate excessive highway noise. The Federal Highway Administration (FHWA) design noise levels are the principal criterion used to determine height and length of a barrier. Most states will not install a barrier unless it will result in a noise reduction of at least 10 dBA (some use 5 dBA as a minimum). Most states use the FHWA model for highway noise prediction, and two thirds of the states design for the most critical receptor. Systematic procedures to obtain data on impacts on residents and motorists are discussed. The perceived effectiveness is often influenced by aesthetics and landscaping of a barrier rather than by acoustical performance. Maintenance problems of barriers include difficulty with mowing close to barriers, litter accumulation, graffiti, and vandalism. Several states have developed priority rating systems for installing noise barriers on existing highways. Design details as well as construction and maintenance aspects are covered in this report. It is recommended that states seek innovative ways to reduce mass of barriers while maintaining noise reduction capability.

**Verdict:** _____

---

##  60. [W98538216](https://openalex.org/W98538216) — 1986 — article — `pre1990`

**Concepts:** Accreditation (0.60), Acceptance testing (0.56), Computer science (0.46), Reliability engineering (0.41), Medical physics (0.35)

**Title:** Technical evaluation of draft ANSI Standard N13. 30, ''performance criteria for radiobioassay''

> The Pacific Northwest Laboratory (PNL) is conducting a research program to evaluate the appropriateness of criteria in the ANSI draft Standard N13.30, ''Performance Criteria for Radiobioassay.'' The evaluation has progressed parallel with the preparation of the Standard by evaluating the performance of existing bioassay laboratories against the criteria specified. Recommendations for revision of the Standard and implementation of a testing/accreditation program have been formulated based on study results. The current performance testing program includes both in-vivo counting and in-vitro sample measurements. Test criteria specified in the Standard include relative bias, relative precision, and acceptable minimum detectable activity (AMDA). Results to date have indicated that the acceptance criteria in the Standard are appropriate for the existing state of the industry and are achievable by a majority of the participating laboratories. Specific conclusions are that the AMDA criteria are most difficult for the laboratories to achieve; the relative bias criterion is second in difficulty, and the precision criterion presents no problem for the laboratories; most of the participating laboratories can meet the Standard; and failure rates may decrease as the laboratories become more knowledgeable of the performance criteria. 3 refs., 11 figs., 6 tabs.

**Verdict:** _____

---

##  61. [W179519192](https://openalex.org/W179519192) — 1963 — article — `pre1990`

**Concepts:** Mass spectrometry (0.75), Molecular beam (0.70), Spectrometer (0.66), Amplifier (0.59), Beam (structure) (0.55)

**Title:** ANALYTICAL MASS SPECTROMETER WITH MODULATED MOLECULAR BEAM

> A mass spectrometer for the analysis of a gas in the form of a molecular beam is described. The apparatus was developed on the basis of the mass spectrometer MS-2M. In the system the formation and modulation of the molecular beam were accomplished directly in the ion source. For measuring the ion current and electronic multiplier was used and the output was switched into an amplifier and a phase-sensitive detector. The sensitivity of the apparatus in the absence of background was 10/sup -3/% but 10/sup -2/% in the presence of background. Use of a modulated beam reduced the background by an order of magnitude. (tr-auth)

**Verdict:** _____

---

##  62. [W2316946868](https://openalex.org/W2316946868) — 1954 — article — `pre1990`

**Concepts:** Wallerian degeneration (0.67), Icon (0.64), Citation (0.63), Library science (0.48), Information retrieval (0.45)

**Title:** Chemical studies of peripheral nerve during Wallerian degeneration. 6. Incorporation of radioactive phosphate into pentosenucleic acid and phospholipin <i>in vitro</i>

> Research Article| October 01 1954 Chemical studies of peripheral nerve during Wallerian degeneration. 6. Incorporation of radioactive phosphate into pentosenucleic acid and phospholipin in vitro W. L. Magee; W. L. Magee 1Department of Biochemistry, University of Western Ontario, London, Canada Search for other works by this author on: This Site PubMed Google Scholar R. J. Rossiter R. J. Rossiter 1Department of Biochemistry, University of Western Ontario, London, Canada Search for other works by this author on: This Site PubMed Google Scholar Author and article information Publisher: Portland Press Ltd © 1954 CAMBRIDGE UNIVERSITY PRESS1954 Biochem J (1954) 58 (2): 243–249. https://doi.org/10.1042/bj0580243 Views Icon Views Article contents Figures & tables Video Audio Supplementary Data Peer Review Share Icon Share Facebook Twitter LinkedIn Email Cite Icon Cite Get Permissions Citation W. L. Magee, R. J. Rossiter; Chemical studies of peripheral nerve during Wallerian degeneration. 6. Incorporation of radioactive phosphate into pentosenucleic acid and phospholipin in vitro. Biochem J 1 October 1954; 58 (2): 243–249. doi: https://doi.org/10.1042/bj0580243 Download citation file: Ris (Zotero) Reference Manager EasyBib Bookends Mendeley Papers EndNote RefWorks BibTex toolbar search Search Dropdown Menu toolbar search search input Search input auto suggest filter your search All ContentAll JournalsBiochemical Journal Search Advanced Search This content is only available as a PDF. © 1954 CAMBRIDGE UNIVERSITY PRESS1954 Article PDF first page preview Close Modal You do not currently have access to this content.

**Verdict:** _____

---

##  63. [W2048608413](https://openalex.org/W2048608413) — 1964 — article — `pre1990`

**Concepts:** Newton's laws of motion (0.88), Law (0.66), Physics (0.64), Impulse (physics) (0.63), Interpretation (philosophy) (0.52)

**Title:** Newton's Laws of Motion and the 17th Century Laws of Impact

> A number of writers on history of science have made it clear that in using the term “motive force” in the “Principia,” Newton referred to what we now call “impulse.” With this interpretation, there is a simple and plausible connection between the laws of impact as they were known and described in Newton's day and Newton's formulation of the Laws of Motion in the “Principia,” and we speculate that Newton might have been motivated by such a perception.

**Verdict:** _____

---

##  64. [W1999634748](https://openalex.org/W1999634748) — 1929 — article — `pre1990`

**Concepts:** Colles' fracture (0.85), Orthodontics (0.44), Computer science (0.37), Medicine (0.34), Anatomy (0.23)

**Title:** AN INVESTIGATION OF THE END-RESULTS OF COLLES'S FRACTURES

> THE following account is based on the examination of about 50 cases of Colles's fracture sustained at least two years previous to our examiniation, in an endeavour to ascertain the causes for the imperfect results that obtain from the ustial methods of treatment at present adopted. Our investigation was made on different lines from those of Edwards and Clayton, whose interesting analysis of 424 fractures of the lower end of the radius in adults appeers in the British MIedical Journal for January 12th (p. 61), but we feel that this account may be of value, particularly when compared with theirs.

**Verdict:** _____

---

##  65. [W4238485385](https://openalex.org/W4238485385) — 1938 — article — `pre1990`

**Concepts:** Pseudonym (1.00), Volume (thermodynamics) (0.57), Art (0.43), Computer science (0.38), Art history (0.37)

**Title:** “Adeline”: Pseudonym

> “Adeline”: Pseudonym Get access A. Mary Kirkus A. Mary Kirkus Search for other works by this author on: Oxford Academic Google Scholar Notes and Queries, Volume 175, Issue 25, 17 December 1938, Page 445, https://doi.org/10.1093/nq/175.25.445d Published: 17 December 1938

**Verdict:** _____

---

##  66. [W1991397619](https://openalex.org/W1991397619) — 1988 — article — `pre1990`

**Concepts:** Publishing (0.66), Library science (0.39), Computer science (0.39), Operations research (0.38), Management (0.32)

**Title:** Artificial Intelligence by Patrick Henry Winston (second edition) Addison-Wesley Publishing Company, Massachusetts, USA, July 1984 (£18.95, student hardback edition)

> An abstract is not available for this content so a preview has been provided. Please use the Get access link above for information on how to access this content.

**Verdict:** _____

---

##  67. [W4233978712](https://openalex.org/W4233978712) — 1987 — report — `pre1990`

**Concepts:** Physics (0.90), Hadron (0.69), Pion (0.68), Annihilation (0.56), Particle physics (0.43)

**Title:** Bose-Einstein correlations in e/sup +/e/sup -/ collisions

> The MARK II detector is used to study the Bose-Einstein correlation between pairs and triplets of charged pions produced in hadronic decays of the J)psi), the ..sqrt..s = 4 to 7 GeV continuum above the J)psi), two photon events at ..sqrt..s = 29 GeV, and e/sup )plus/)e/sup )minus/) annihilation events at ..sqrt..s = 29 GeV as a function of Q/sup 2/, the four-momentum transfer squared. After corrections for Coulomb effects and pion misidentification, we find a nearly full Bose-Einstein enhancement ..cap alpha.. in the J)psi) and the two photon data and about half the maximum value in the other two data sets. The radius parameter )tau)(an average over space and time) given by pion pair analyses lies within a band of +-0.10 fm around 0.73 fm and is the same, within errors, for all four data sets. Pion triplet analyses also give a consistent radius of approx. 0.54 fm. fits to two-dimensional distributions R(q/sub T//sup 2/, q/sub C//sup 2/) of invariant components of Q/sup 2/ = q/sub T//sup 2/ )plus) q/sub C//sup 2/ give )tau)/sub T/ approx. )tau)C approx. )tau), where q/sub T/ is the transverse three-momentum difference calculated with respect to the net pair three-momentum, and q/sub C/ is in effect the longitudinal three-momentum difference in the pion pair rest frame. When q/sub T/ is calculated with respect to the jet axis for two-jet events in the e/sup )plus/)e/sup )minus/) annihilation data at ..sqrt..s = 29 GeV, a fit to R(q/sub T//sup 2/, q/sub C//sup 2/) also gives )tau)/sub T/ approx. )tau)/sub C/ approx. )tau). Noting that q/sub L/ and q/sub 0/ are not invariant, we make fits to R(/sub T//sup T/, q/sub L//sup 2/) and to R(q/sub T//sup 2/, q/sub 0//sup 2/) (Kopylov formulation), and we find )tau)/sub 0/ approx. )tau)/sub L/ approx. )23))tau)/sub T/ to )12))tau)/sub T/. 44 refs., 43 figs., 15 tabs

**Verdict:** _____

---

##  68. [W754692244](https://openalex.org/W754692244) — 1978 — book — `pre1990`

**Concepts:** Plan (archaeology) (0.49), Computer science (0.34), Geography (0.23), Archaeology (0.07)

**Title:** Clatskanie : Comprehensive plan (1978)

> 86 pp. Bookmarks supplied by UO. Map, charts. Published July, 1978. Scanned by UO from item HT168 .C53 S54 1978, May, 2009.

**Verdict:** _____

---

##  69. [W2789153476](https://openalex.org/W2789153476) — 1934 — article — `pre1990`

**Concepts:** Philosophy (0.65), Humanities (0.62), Physics (0.36)

**Title:** Sensibilitat a les Tuberculines Antiga de Koch i B.C.G. en nens que han ingerit vacuna B.C.G. durant els deu primers dies de la seva vida i permaneixent en un medi suposat indemne

> espanolComparando las reacciones obtenidas para precisar la sensibilidad de - la tuberculina antigua i la tuberculina B. C. G., observan: Que el nino vacunado con B. C. G. por via oral es mas sensible a la tuberculina de este bacilo que a la antigua de Koch ; Que es mayor el numero de reacciones positivas fugaces empleando, tuberculina B. C. G.; Que estas reacciones aumentan al aumentar la concentracion de las soluciones empleadas. Se podria aun anadir, junto con otros'observadores,.que la precocidad y fugacidad de las reacciones son propias de los medios sanos; asi como la persistencia lo es de los medios infectados. francaisEn comparant les reactions obtenues pour preciser la sensibilite de la tuberculine ancienne et la tuberculine B. C. G. il observe : Que l'enfant vaccine avec B. C. G. par voie orale est plus sensible a la tuberculine de ce bacille qu'a, l'encienne de Koch; Que le nombre de reactions fugaces est superieur en employant la tuberculine B. C. G.; Que ces reactions augmentent quand augmente la concentration des solutions employees. On pourrait ajouter, avec les observateurs, que la precocite et fugacite des reactions somit .propres des millieux sains; ainsi que la persistence l'est, des millieus infectes.

**Verdict:** _____

---

##  70. [W4303078340](https://openalex.org/W4303078340) — 1915 — article — `pre1990`

**Concepts:** Icon (0.97), Citation (0.57), Download (0.54), Information retrieval (0.45), Computer science (0.43)

**Title:** The Belgian Soldier

> Essay| March 01 1915 The Belgian Soldier Current History (1915) 1 (6): 1215–1216. https://doi.org/10.1525/curh.1915.1.6.1215 Views Icon Views Article contents Figures & tables Video Audio Supplementary Data Peer Review Share Icon Share Twitter LinkedIn Tools Icon Tools Get Permissions Cite Icon Cite Search Site Citation The Belgian Soldier. Current History 1 March 1915; 1 (6): 1215–1216. doi: https://doi.org/10.1525/curh.1915.1.6.1215 Download citation file: Ris (Zotero) Reference Manager EasyBib Bookends Mendeley Papers EndNote RefWorks BibTex toolbar search Search Dropdown Menu toolbar search search input Search input auto suggest filter your search All ContentCurrent History Search This content is only available via PDF. © 1915 by The Regents of the University of California1915 Article PDF first page preview Close Modal You do not currently have access to this content.

**Verdict:** _____

---

##  71. [W1654257636](https://openalex.org/W1654257636) — 1973 — article — `pre1990`

**Concepts:** Computer science (0.31)

**Title:** 19世紀イギリス金本位制における国際収支調整メカニズム--A.G.フォードの分析を中心にして

> ? ( 1 ) l l = ( 2 ) () ( 3 ) D 1 9 ( 1 8 8 0 -1 9 1 4 1 9 ) ( 1 ) ( 4 ) ( 2 ) A G F o r d ; The g o l d S t a n d a r d 1 8 8 0 ' " ' -' 1 9 1 4 ; B r i t a i n a n d A r g e n t i n a ) O x f o r d ) 1 9 6 2 4i 7t ( 5 ) O () ( 1 ) A HH a n s e n T h e D o l l a r a n d T h e I n t e r n a t i o n a l M o n e t a r y S y s t e m 1 9 6 5J3 0 -----3 1 ( 2 ) j = () = 1

**Verdict:** _____

---

##  72. [W2571345580](https://openalex.org/W2571345580) — 1983 — article — `pre1990`

**Concepts:** Physics (0.88), Planetary nebula (0.76), Astrophysics (0.69), Photometry (optics) (0.57), Astronomy (0.50)

**Title:** Two-dimensional photometry of planetary nebulae

> In connection with the study of planetary nebulae, problems still exist in understanding such basic properties as three-dimensional structure, optical opacity to the central star's ionizing flux, and electron temperature and electron density variations within the nebular gas. To study these properties, two-dimensional images taken in many spectral lines are required. However, such a study presents a formidable problem in data analysis. In the present investigation, an attempt has been made to overcome the difficulties by using an imaging system which encodes the data digitally. Calibrated intensity maps could be constructed to test models of ionization structure and to produce two-dimensional maps of electron temperature and density. Both the results of a uniform-shell test and the nature of the solutions for the volume emissivity were found to support a nebular model in which the bright ring is part of a closed shell of variable density that resembles the torus proposed by Minkowski and Osterbrock (1960).

**Verdict:** _____

---

##  73. [W2061271773](https://openalex.org/W2061271773) — 1969 — article — `pre1990`

**Concepts:** Citation (0.65), Altmetrics (0.64), Potentiometric titration (0.64), Icon (0.48), Titration (0.47)

**Title:** Potentiometric titration of stereoregular poly(acrylic acids)

> ADVERTISEMENT RETURN TO ISSUEPREVArticleNEXTPotentiometric titration of stereoregular poly(acrylic acids)Yoshikazu Kawaguchi and Mitsuru NagasawaCite this: J. Phys. Chem. 1969, 73, 12, 4382–4384Publication Date (Print):December 1, 1969Publication History Published online1 May 2002Published inissue 1 December 1969https://pubs.acs.org/doi/10.1021/j100846a065https://doi.org/10.1021/j100846a065research-articleACS PublicationsRequest reuse permissionsArticle Views271Altmetric-Citations29LEARN ABOUT THESE METRICSArticle Views are the COUNTER-compliant sum of full text article downloads since November 2008 (both PDF and HTML) across all institutions and individuals. These metrics are regularly updated to reflect usage leading up to the last few days.Citations are the number of other articles citing this article, calculated by Crossref and updated daily. Find more information about Crossref citation counts.The Altmetric Attention Score is a quantitative measure of the attention that a research article has received online. Clicking on the donut icon will load a page at altmetric.com with additional details about the score and the social media presence for the given article. Find more information on the Altmetric Attention Score and how the score is calculated. Share Add toView InAdd Full Text with ReferenceAdd Description ExportRISCitationCitation and abstractCitation and referencesMore Options Share onFacebookTwitterWechatLinked InRedditEmail Other access options Get e-Alerts

**Verdict:** _____

---

##  74. [W4312760180](https://openalex.org/W4312760180) — 1985 — article — `pre1990`

**Concepts:** Icon (0.87), Citation (0.71), Download (0.67), Publishing (0.44), History (0.43)

**Title:** The Old Folks Day: A Unique Utah Tradition

> Research Article| April 01 1985 The Old Folks Day: A Unique Utah Tradition JOSEPH HEINERMAN JOSEPH HEINERMAN Search for other works by this author on: This Site Google Utah Historical Quarterly (1985) 53 (2): 157–169. https://doi.org/10.2307/45061206 Cite Icon Cite Share Icon Share Facebook Twitter LinkedIn MailTo Permissions Search Site Citation JOSEPH HEINERMAN; The Old Folks Day: A Unique Utah Tradition. Utah Historical Quarterly 1 January 1985; 53 (2): 157–169. doi: https://doi.org/10.2307/45061206 Download citation file: Zotero Reference Manager EasyBib Bookends Mendeley Papers EndNote RefWorks BibTex toolbar search Search Dropdown Menu toolbar search search input Search input auto suggest filter your search All Scholarly Publishing CollectiveUniversity of Illinois PressUtah Historical Quarterly Search Advanced Search The text of this article is only available as a PDF. © Copyright 1985 Utah State Historical Society1985 Article PDF first page preview Close Modal You do not currently have access to this content.

**Verdict:** _____

---

##  75. [W160089336](https://openalex.org/W160089336) — 1975 — article — `pre1990`

**Concepts:** Sampling (signal processing) (0.77), Computer science (0.58), Quality (philosophy) (0.56), Process (computing) (0.54), Simple random sample (0.51)

**Title:** Sampling from Batches

> The outputs of many manufacturing processes consist of batches which tend to be more homogeneous than the outputs from the process as a whole. Thus the quality of just one batch is not necessarily representative of the long term quality of the process. This paper discusses a two stage plan for obtaining representative samples of the outputs of such manufacturing processes. The two stage plan is both more efficient and more convenient than simple random sampling. The plan entails sampling k of the batches and subsampling m units within each of the sampled batches. Formulas are presented which determine how k and m should be chosen to maximize the sampling precision subject to cost constraints. Several numerical examples illustrate the adverse effect on precision due to sampling from too few batches. In particular it is shown that drawing the entire sample from just one batch leads to very poor precision.

**Verdict:** _____

---

##  76. [W7103282272](https://openalex.org/W7103282272) — 1974 — other — `pre1990`

**Concepts:** Scripting language (0.68), Computer science (0.44), World Wide Web (0.41), Exposition (narrative) (0.35), History (0.35)

**Title:** NBC News Scripts

> Script from the WBAP-TV/NBC station in Fort Worth, Texas, relating a news story about an unidentified man who was dead on arrival at John Peter Smith hospital.

**Verdict:** _____

---

##  77. [W2046099298](https://openalex.org/W2046099298) — 1955 — article — `pre1990`

**Concepts:** Citation (0.75), Altmetrics (0.75), Computer science (0.59), Icon (0.58), Social media (0.53)

**Title:** Dehydration of Orthophosphoric Acid

> ADVERTISEMENT RETURN TO ISSUEPREVArticleNEXTDehydration of Orthophosphoric AcidC. E. Higgins and W. H. BaldwinCite this: Anal. Chem. 1955, 27, 11, 1780–1783Publication Date (Print):November 1, 1955Publication History Published online1 May 2002Published inissue 1 November 1955https://pubs.acs.org/doi/10.1021/ac60107a030https://doi.org/10.1021/ac60107a030research-articleACS PublicationsRequest reuse permissionsArticle Views562Altmetric-Citations31LEARN ABOUT THESE METRICSArticle Views are the COUNTER-compliant sum of full text article downloads since November 2008 (both PDF and HTML) across all institutions and individuals. These metrics are regularly updated to reflect usage leading up to the last few days.Citations are the number of other articles citing this article, calculated by Crossref and updated daily. Find more information about Crossref citation counts.The Altmetric Attention Score is a quantitative measure of the attention that a research article has received online. Clicking on the donut icon will load a page at altmetric.com with additional details about the score and the social media presence for the given article. Find more information on the Altmetric Attention Score and how the score is calculated. Share Add toView InAdd Full Text with ReferenceAdd Description ExportRISCitationCitation and abstractCitation and referencesMore Options Share onFacebookTwitterWechatLinked InRedditEmail Other access optionsGet e-Alertsclose Get e-Alerts

**Verdict:** _____

---

##  78. [W2767151332](https://openalex.org/W2767151332) — 1983 — article — `pre1990`

**Concepts:** Computer science (0.45), Engineering (0.42), Engineering drawing (0.41), Mechanical engineering (0.40), Automotive engineering (0.38)

**Title:** Design And Calculation Methods For High-Speed Gears Of Advanced Technology.

> High-speed gears of very high powers and/or very high speeds must be exactly analyzed and optimized in gearing, bearing and housing in order to achieve low noise, low vibra tion running with maximum safety in operation.The gearing must be checked by detailed calculations in load capacity, including an exact analysis of the scoring safety.Special design means must be applied in order to cover thermal problems at the gearing.Besides this, the calculation and design of the plain bear ings are of main interest.They also must be analyzed in detail, not only in general hydrodynamic load capacity, but also in their real temperature and pressure conditions in the oil film.The design of the plain bearing then has to be adapted to its vibration behaviour.Using modern CAE methods, the design process can be made faster and safer.Practical examples of some of the highest-powered high-speed gears of the world prove the methods used in design, calculations and manufacturii).g.

**Verdict:** _____

---

##  79. [W4242422561](https://openalex.org/W4242422561) — 1967 — article — `pre1990`

**Concepts:** Vibration (0.79), Impulse (physics) (0.59), Natural frequency (0.50), Femur (0.50), Acoustics (0.44)

**Title:** On a Bone-Vibration

> This experiment is one step to clarify dynamic mechanical properties of bones, especially femurs.Material: four dry femurs.We designed a method that a mechanical impulse was exerted on a femoral head along the functional axis of femur with a pendulum. Then a femur, whose condyle is fixed and head is free, is placed horizontally.When a mechanical impulse was exerted on a femur in the above position, a bone vibration was developed. This vibration was analyzed, and was similar to a summation of a high- and a low-frequency component. Therefore, we picked out separately the high- and the low-frequency component with a filter circuit. There were vibrations with logarithmic decrement. The vibrations had a natural frequency themselves—the high was about 500cps and the low was about 100cps.Now, a solution of a sort of a second-order differential equation Md2x/dt2+Sdx/dt+Kx=F(t)is also a damping vibration with logarithmic decrement. Then, we added two second-order differential equations with two different constant coefficients, using a desk-top ANALOG computor. Using this solution yielded a similar wave to a bone vibration.Therefore, we think now that a bone vibration under the above conditions may be expressed as a summation of two ordinary second-order differential equations.Furthermore, analysing many more bone-vibrations, we will compare the difference of the damping ratio and the natural frequency of vibration between many bones.

**Verdict:** _____

---

##  80. [W2328085696](https://openalex.org/W2328085696) — 1942 — article — `pre1990`

**Concepts:** Icon (0.76), Citation (0.73), Altmetrics (0.59), Social media (0.48), Computer science (0.47)

**Title:** The Nitration of 4-Phenylphenyl Benzoate

> ADVERTISEMENT RETURN TO ISSUEPREVArticleNEXTThe Nitration of 4-Phenylphenyl BenzoateStewart E. Hazlet and Harris O. Van OrdenCite this: J. Am. Chem. Soc. 1942, 64, 10, 2505–2506Publication Date (Print):October 1, 1942Publication History Published online1 May 2002Published inissue 1 October 1942https://pubs.acs.org/doi/10.1021/ja01262a510https://doi.org/10.1021/ja01262a510research-articleACS PublicationsRequest reuse permissionsArticle Views50Altmetric-Citations-LEARN ABOUT THESE METRICSArticle Views are the COUNTER-compliant sum of full text article downloads since November 2008 (both PDF and HTML) across all institutions and individuals. These metrics are regularly updated to reflect usage leading up to the last few days.Citations are the number of other articles citing this article, calculated by Crossref and updated daily. Find more information about Crossref citation counts.The Altmetric Attention Score is a quantitative measure of the attention that a research article has received online. Clicking on the donut icon will load a page at altmetric.com with additional details about the score and the social media presence for the given article. Find more information on the Altmetric Attention Score and how the score is calculated. Share Add toView InAdd Full Text with ReferenceAdd Description ExportRISCitationCitation and abstractCitation and referencesMore Options Share onFacebookTwitterWechatLinked InRedditEmail Other access optionsGet e-Alertsclose Get e-Alerts

**Verdict:** _____

---

##  81. [W4242941594](https://openalex.org/W4242941594) — 1726 — article — `pre1990`

**Concepts:** Pendulum (0.70), Action (physics) (0.66), Notice (0.54), Motion (physics) (0.47), Physics (0.39)

**Title:** IV. A contrivance to avoid the irregularities in a clocks motion, occasion'd by the action of heat and cold upon the rod of the pendulum

> Abstract Whereas several, who have been curious in measuring of time, have taken notice, that the vibrations of a pendulum are slower in summer than in winter; and have very justly supposed this alteration has proceeded from a change of length in the pendulum itself, by the influences of heat and cold upon it, in the different seasons of the year

**Verdict:** _____

---

##  82. [W2498849574](https://openalex.org/W2498849574) — 1950 — article — `pre1990`

**Concepts:** Electron (0.79), Transistor (0.70), Semiconductor (0.69), Silicon (0.66), Electronics (0.54)

**Title:** The behavior of holes and electrons in semiconductors

> “Holes” and “electrons” are words used to describe the two processes by which electrons carry current in semiconductors like silicon and germanium. These two processes, although prominent in theory for the last two decades, have acquired much greater reality as a result of new experiments stemming from the invention of the transistor. In fact a new engineering science, referred to as transistor electronics, is now being built about the behavior of holes and electrons.

**Verdict:** _____

---

##  83. [W2012595710](https://openalex.org/W2012595710) — 1987 — article — `pre1990`

**Concepts:** Icon (0.96), Download (0.75), Citation (0.69), Perspective (graphical) (0.49), Register (sociolinguistics) (0.47)

**Title:** The National Register of Historic Places: A Personal Perspective on the First Twenty Years

> Research Article| April 01 1987 The National Register of Historic Places: A Personal Perspective on the First Twenty Years Jerry L. Rogers Jerry L. Rogers Search for other works by this author on: This Site PubMed Google Scholar The Public Historian (1987) 9 (2): 91–104. https://doi.org/10.2307/3377332 Views Icon Views Article contents Figures & tables Video Audio Supplementary Data Peer Review Share Icon Share Facebook Twitter LinkedIn MailTo Tools Icon Tools Get Permissions Cite Icon Cite Search Site Citation Jerry L. Rogers; The National Register of Historic Places: A Personal Perspective on the First Twenty Years. The Public Historian 1 April 1987; 9 (2): 91–104. doi: https://doi.org/10.2307/3377332 Download citation file: Ris (Zotero) Reference Manager EasyBib Bookends Mendeley Papers EndNote RefWorks BibTex toolbar search Search Dropdown Menu toolbar search search input Search input auto suggest filter your search All ContentThe Public Historian Search This content is only available via PDF. Copyright 1987 The Regents of the University of California Article PDF first page preview Close Modal You do not currently have access to this content.

**Verdict:** _____

---

##  84. [W2104225190](https://openalex.org/W2104225190) — 1979 — article — `pre1990`

**Concepts:** Microstrip antenna (0.73), Microstrip (0.58), Radiation pattern (0.56), Radiation (0.50), Physics (0.49)

**Title:** A model for calculating the radiation field of microstrip antennas

> Starting from the equivalence principle, an aperture model is developed for calculating the radiation field of microstrip antennas. In this communication the model is applied to the rectangular microstrip resonator antenna. Antenna characteristics, like patterns and radiation resistance, are computed and compared with experimental results. The model and the calculations include the higher order modes as well as the fundamental mode of the resonator antenna.

**Verdict:** _____

---

##  85. [W1482436422](https://openalex.org/W1482436422) — 1971 — article — `pre1990`

**Concepts:** Physics (0.68), Spurious relationship (0.68), Nonlinear system (0.66), Quadrupole (0.66), Scattering (0.65)

**Title:** OBSERVATIONS OF NONLINEAR SCATTERING FROM A PLASMA COLUMN.

> Nonlinear interaction effects are considered for signals incident on an unmagnetized cold plasma column, without making the quasi-static approximation. It is found that the nonlinearly generated quadrupole component is only modified slightly and that no multipolar component can give a forward- or back-scattered signal. However, strong nonlinear forward scattering was observed in previous experiments. This spurious result has been traced to the effect of the earth's magnetic field. When this is cancelled, predominantly quadrupolar radiation is observed, in agreement with theory.

**Verdict:** _____

---

##  86. [W7005016568](https://openalex.org/W7005016568) — 1952 — article — `pre1990`

**Concepts:** Computer science (0.37), History (0.26), Sociology (0.25), Subject (documents) (0.23), Column (typography) (0.22)

**Title:** Personal Papers (MS 80-0002)

> Account Statements from Maison Glass prepared for D. W. Kempner. The statements include item descriptions and charges.

**Verdict:** _____

---

##  87. [W7051861802](https://openalex.org/W7051861802) — 1968 — other — `pre1990`

**Concepts:** EPIC (0.52), Convention (0.52), Portrait (0.49), Performing arts (0.43), Art (0.35)

**Title:** Photograph of Tammy Wynette, circa 1968

> A portrait of country music performer Tammy Wynette. She performed at the 1968 Gala Show ending the Epic Convention in Las Vegas.

**Verdict:** _____

---

##  88. [W2033143906](https://openalex.org/W2033143906) — 1983 — article — `pre1990`

**Concepts:** Actuary (0.79), Computer science (0.54), Business (0.19), Finance (0.11)

**Title:** A day in the life of a new-generation computer user

> This is a fictional account of how the next generation of computers might help a user on a typical day in 1993. All technologies mentioned have already been demonstrated as research prototypes; only the specific machines and situations are fictional projections. In the scenario, the user, John Atarashi, is an actuary working for a company that develops retirement benefit plans for client companies around the world.

**Verdict:** _____

---

##  89. [W2007687569](https://openalex.org/W2007687569) — 1987 — article — `pre1990`

**Concepts:** Physics (0.91), Astrophysics (0.67), Shock wave (0.64), Radiative cooling (0.61), Star formation (0.60)

**Title:** Hydrogen molecules and the radiative cooling of pregalactic shocks

> The nonequilibrium radiative cooling, recombination, and molecule formation behind steady state shock waves in a gas of primordial composition have been calculated in detail for a number of cases. The authors have solved the rate equations for these processes, together with the hydrodynamical conservation equations. Such shock waves are relevant to a wide range of theories of galaxy and pregalactic star formation. A purely atomic gas of H and He which is shock-heated to temperatures above 10<SUP>4</SUP>K is assumed. The results indicate that formation of H<SUB>2</SUB> molecules in the post-shock gas may be quite common for a significant range of shock velocities. The extra cooling resulting from H<SUB>2</SUB> formation greatly reduces previous estimates of the characteristic gravitational scale length and the characteristic mass subject to gravitational instability in these postshock regions.

**Verdict:** _____

---

##  90. [W7018815781](https://openalex.org/W7018815781) — 1874 — other — `pre1990`

**Concepts:** Physics (0.35), Context (archaeology) (0.22), Philosophy (0.20), Geology (0.20), Term (time) (0.19)

**Title:** Dostateczny śpiewnik kościelny i domowy wraz z książką modlitewną, dla wygody katolików z różnych książek i śpiewników zebrany i ułożony polecony przez Melchiora de Diepenbrock i Daniela Latussek

> Polecenia Biskupie.Koci Chrystusw odznacza si od wszystkich innych wyzna, ktre z czasem powstay, je d n o s ta jn o c i tak w odprawianiu bezkrwawej Ofiary Mszy . jako i w udzie laniu Sakramentw S

**Verdict:** _____

---

##  91. [W597279077](https://openalex.org/W597279077) — 1971 — article — `pre1990`

**Concepts:** Inviscid flow (0.86), Turbulence (0.80), Boundary layer (0.79), Mechanics (0.64), Boundary (topology) (0.58)

**Title:** Some characteristics of turbulent boundary layers in rapidly accelerated flows

> An analysis of time-mean-turbulent boundary layer velocity profiles measured in a rapidly accelerating flow suggests that the outer region of the velocity profiles consists of essentially inviscid, rotational flow. The extent of this inviscid outer region was observed in some cases to exceed 90 percent of what is ordinarily thought of as the turbulent boundary layer thickness. On the other hand, the inner frictional region of these velocity profiles appears to have turbulent characteristics similar to those of more conventional turbulent boundary layers. Hence, the outer edge boundary condition for this inner region is more properly the external rotational flow region than the free stream.

**Verdict:** _____

---

##  92. [W4205391401](https://openalex.org/W4205391401) — 1953 — article — `pre1990`

**Concepts:** Citation (0.71), Icon (0.59), Social media (0.54), Computer science (0.53), Altmetrics (0.49)

**Title:** NOW... available from Du Pont

> RETURN TO ISSUEPREVAdvertisementNEXTNOW... available from Du PontCite this: Chem. Eng. News 1953, 31, 43, 4461Publication Date (Print):October 26, 1953Publication History Published online12 November 2010Published inissue 26 October 1953https://doi.org/10.1021/cen-v031n043.p4461Copyright © 1953 AMERICAN CHEMICAL SOCIETYArticle Views3Altmetric-Citations-LEARN ABOUT THESE METRICSArticle Views are the COUNTER-compliant sum of full text article downloads since November 2008 (both PDF and HTML) across all institutions and individuals. These metrics are regularly updated to reflect usage leading up to the last few days.Citations are the number of other articles citing this article, calculated by Crossref and updated daily. Find more information about Crossref citation counts.The Altmetric Attention Score is a quantitative measure of the attention that a research article has received online. Clicking on the donut icon will load a page at altmetric.com with additional details about the score and the social media presence for the given article. Find more information on the Altmetric Attention Score and how the score is calculated. Share Add toView InAdd Full Text with ReferenceAdd Description ExportRISCitationCitation and abstractCitation and referencesMore Options Share onFacebookTwitterWechatLinked InReddit PDF (69 KB) Get e-Alerts

**Verdict:** _____

---

##  93. [W2112928867](https://openalex.org/W2112928867) — 1962 — book — `pre1990`

**Concepts:** Statistical inference (0.62), Inference (0.57), Epistemology (0.37), Computer science (0.36), Statistics (0.24)

**Title:** On the Foundations of Statistical Inference: Discussion

> L. J. Savage, George Barnard, Jerome Cornfield, Irwin Bross, George E. P. Box, I. J. Good, D. V. Lindley, C. W. Clunies-Ross, John W. Pratt, Howard Levene, Thomas Goldman, A. P. Dempster, Oscar Kempthorne, Allan Birnbaum, On the Foundations of Statistical Inference: Discussion, Journal of the American Statistical Association, Vol. 57, No. 298 (Jun., 1962), pp. 307-326

**Verdict:** _____

---

##  94. [W4240039616](https://openalex.org/W4240039616) — 1980 — article — `pre1990`

**Concepts:** Flocculation (0.96), Computer science (0.38), Environmental science (0.26), Environmental engineering (0.16)

**Title:** Flocculation — which factors influence it? — Part I

> “Flocculation” is a generally unloved characteristic of pigmented systems. The question in the title, however, presumes that one knows what flocculation is. But if one asks various competent people: “What is flocculation?”, then one receives not only similar replies, but frequently also different descriptions and definitions with which the persons asked generally characterise their specific problem‐areas. This situation shows that flocculation is an expression with various meanings describing both causes and effects in differing forms. This fact, however, involves various risks and indeed difficulties in communication.

**Verdict:** _____

---

##  95. [W2019469205](https://openalex.org/W2019469205) — 1985 — article — `pre1990`

**Concepts:** Citation (0.77), Computer science (0.70), Code (set theory) (0.64), Corporation (0.60), Generator (circuit theory) (0.56)

**Title:** A unified code generator for multiple architectures

> Article Free Access Share on A unified code generator for multiple architectures Author: Sarah Rymal McKie Sperry corporation, Roseville, Minnesota Sperry corporation, Roseville, MinnesotaView Profile Authors Info & Claims ACM '85: Proceedings of the 1985 ACM annual conference on The range of computing : mid-80's perspective: mid-80's perspectiveOctober 1985 Pages 412–416https://doi.org/10.1145/320435.320552Online:01 October 1985Publication History 0citation101DownloadsMetricsTotal Citations0Total Downloads101Last 12 Months2Last 6 weeks1 Get Citation AlertsNew Citation Alert added!This alert has been successfully added and will be sent to:You will be notified whenever a record that you have chosen has been cited.To manage your alert preferences, click on the button below.Manage my AlertsNew Citation Alert!Please log in to your account Save to BinderSave to BinderCreate a New BinderNameCancelCreateExport CitationPublisher SiteeReaderPDF

**Verdict:** _____

---

##  96. [W1990743634](https://openalex.org/W1990743634) — 1988 — article — `pre1990`

**Concepts:** Physics (0.89), Astrophysics (0.74), Radiative transfer (0.61), Spectral line (0.57), Absorption (acoustics) (0.53)

**Title:** H I emission-absorption studies with high-velocity resolution

> The properties of interstellar H I are investigated using high-velocity resolution, Arecibo emission-absorption spectra in the direction of 40 radio continuum sources, including 21 at low galactic latitude. This data is compared with previous Arecibo data at intermediate and high galactic latitude to rediscuss some uncertainties in the analysis of H I spectra due to radiative transfer effects, nonzero beamwidth and a nonuniform H I distribution. This comparison corroborates (a) the earlier suggestion that the H I density in the nearest 100 pc is lower than the disk average by about a factor of 2 and (b) the previous separation of H I emission into material associated with absorbing "clouds" and physically independent, not strongly absorbing (INSA) material, each type containing ~50% by mass. A comparison of lines of sight with different geometries supports the previous suggestion that spin temperatures are higher far above the galactic disk. There is little correlation between the properties of the H I emission fluctuations on 3.8' separations and the properties of either the emission or the absorption profiles. Analysis of the high latitude spectra shows that Gaussian fits provide an excellent description of the H I absorption profiles. An observed lack of structure in the absorption profiles with a line width less than 0.5 km s^-1^ indicates that hypothetical cold H I clumps have column densities less than 5 x l0^18^ cm^-2^. From a comparison of H I and OH spectra, it is inferred that the H I in molecular clumps is less than a few percent of the total hydrogen present.

**Verdict:** _____

---

##  97. [W2083252160](https://openalex.org/W2083252160) — 1988 — article — `pre1990`

**Concepts:** Computer science (0.49), Service (business) (0.46), World Wide Web (0.41), Scope (computer science) (0.41), Telecommunications (0.38)

**Title:** Reaching out to the end user with the BIOSIS Connection

> The Biosis Connection was launched on 2 May 1988, as an online search system targeted to research scientists in the life sciences. Since there is no professional society dedicated to serving life scientists as an integrated group, Biosis saw a need to facilitate communications between life scientists by becoming the focal point of information services for this community. Biosis undertook this project well aware of the ‘elusive end user’ phenomenon. Biosis carefully researched ways and means to serve this audience as a first step in achieving the long term goals of the Biosis Connection. The resulting system design and specifications took into account the fact that virtually every successful electronic end user product on the market must appeal to the professional librarian as well. To that end, the Biosis Connection was designed with both a menu‐driven front end package to serve the novice or occasional user in addition to a command language version for the experienced user and/or information professional. The databases included for initial offering were selected to meet current awareness needs or to allow access to databases unavailable on any other online system. None of these compete directly with any other Biosis online database. System enhancements and the development of new databases are ongoing activities, with the first upgrades scheduled for implementation in the fall of 1988. Companion services for document ordering and event referral were incorporated from the start so that the Biosis Connection would be a complete information service. The project scope to start up the Biosis Connection was equivalent to that of establishing a new business. In this paper, the planning, project research and product development processes are examined. The effectiveness of Beta testing the system will also be reviewed. Preliminary market response and formal evaluations received are summarized. Finally, a brief discussion of the highlights and lowlights of building a system like the Biosis Connection is given.

**Verdict:** _____

---

##  98. [W6988060183](https://openalex.org/W6988060183) — 1949 — other — `pre1990`

**Concepts:** Series (stratigraphy) (0.33), Computer science (0.30), Philosophy (0.29), Natural (archaeology) (0.23), Set (abstract data type) (0.23)

**Title:** What Would You Do If...? Part VI

> Part six of six in a series about practical nonresistance published in the Youth's Christian Companion under the name "Ein Wiedertaüfer."

**Verdict:** _____

---

##  99. [W4243042883](https://openalex.org/W4243042883) — 1958 — paratext — `pre1990`

**Concepts:** Computer science (0.33)

**Title:** [no title]

> CA: A Cancer Journal for Clinicians publishes information about the prevention, early detection, and treatment of cancer, as well as nutrition, palliative care, survivorship, and additional topics of interest related to cancer care.

**Verdict:** _____

---

## 100. [W4249560544](https://openalex.org/W4249560544) — 1979 — article — `pre1990`

**Concepts:** Citation (0.73), Altmetrics (0.71), Icon (0.69), Social media (0.58), Computer science (0.57)

**Title:** McPherson Instruments

> ADVERTISEMENT RETURN TO ISSUEPREVArticleNEXTMcPherson InstrumentsCite this: Anal. Chem. 1979, 51, 8, 882APublication Date (Print):July 1, 1979Publication History Published online25 May 2012Published inissue 1 July 1979https://doi.org/10.1021/ac50044a776RIGHTS & PERMISSIONSArticle Views8Altmetric-Citations-LEARN ABOUT THESE METRICSArticle Views are the COUNTER-compliant sum of full text article downloads since November 2008 (both PDF and HTML) across all institutions and individuals. These metrics are regularly updated to reflect usage leading up to the last few days.Citations are the number of other articles citing this article, calculated by Crossref and updated daily. Find more information about Crossref citation counts.The Altmetric Attention Score is a quantitative measure of the attention that a research article has received online. Clicking on the donut icon will load a page at altmetric.com with additional details about the score and the social media presence for the given article. Find more information on the Altmetric Attention Score and how the score is calculated. Share Add toView InAdd Full Text with ReferenceAdd Description ExportRISCitationCitation and abstractCitation and referencesMore Options Share onFacebookTwitterWechatLinked InReddit PDF (807 KB) Get e-Alerts Get e-Alerts

**Verdict:** _____

---
