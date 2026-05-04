# Phase 0.2 Wave 1B — NamSor 50-name × 6-region smoke

**Run date:** 2026-05-04
**Snapshot:** 2026-05-04T21:39:00+00:00
**API:** NamSor v2 /genderBatch
**Wall-clock:** 1.0s for 48 names

## Per-region accuracy

| Region | N | Resolved | Match expected | Rate | p_calibrated mean | p_calibrated min |
|---|---:|---:|---:|---:|---:|---:|
| anglo | 8 | 8 | 8 | 1.000 | 0.985 | 0.977 |
| arabic | 8 | 8 | 8 | 1.000 | 0.987 | 0.967 |
| east_asian | 8 | 8 | 6 | 0.750 | 0.805 | 0.527 |
| other | 8 | 8 | 8 | 1.000 | 0.970 | 0.847 |
| slavic | 8 | 8 | 8 | 1.000 | 0.996 | 0.991 |
| south_asian | 8 | 8 | 8 | 1.000 | 0.984 | 0.956 |

## Per-name table

| ID | Region | Name | Expected | Predicted | Score | p_cal | Match? |
|---|---|---|---|---|---:|---:|---|
| anglo_01 | anglo | John Smith | male | male | 12.978 | 0.994 | ✅ |
| anglo_02 | anglo | Mary Johnson | female | female | 10.791 | 0.986 | ✅ |
| anglo_03 | anglo | James Williams | male | male | 10.890 | 0.986 | ✅ |
| anglo_04 | anglo | Patricia Brown | female | female | 13.252 | 0.994 | ✅ |
| anglo_05 | anglo | Robert Jones | male | male | 8.027 | 0.979 | ✅ |
| anglo_06 | anglo | Jennifer Davis | female | female | 4.839 | 0.980 | ✅ |
| anglo_07 | anglo | Michael Miller | male | male | 8.529 | 0.977 | ✅ |
| anglo_08 | anglo | Linda Wilson | female | female | 10.507 | 0.985 | ✅ |
| easian_01 | east_asian | Wei Zhang | male | female | 1.199 | 0.527 | ❌ |
| easian_02 | east_asian | Mei Chen | female | female | 3.229 | 0.916 | ✅ |
| easian_03 | east_asian | Hiroshi Tanaka | male | male | 9.619 | 0.990 | ✅ |
| easian_04 | east_asian | Yuki Sato | female | male | 0.110 | 0.737 | ❌ |
| easian_05 | east_asian | Min-jun Kim | male | male | 3.097 | 0.728 | ✅ |
| easian_06 | east_asian | Ji-hye Park | female | female | 7.098 | 0.935 | ✅ |
| easian_07 | east_asian | Jun Wang | male | male | 2.225 | 0.760 | ✅ |
| easian_08 | east_asian | Xiu Liu | female | female | 3.520 | 0.845 | ✅ |
| sasian_01 | south_asian | Raj Patel | male | male | 7.349 | 0.956 | ✅ |
| sasian_02 | south_asian | Priya Sharma | female | female | 12.138 | 0.991 | ✅ |
| sasian_03 | south_asian | Arjun Kumar | male | male | 13.211 | 0.994 | ✅ |
| sasian_04 | south_asian | Aisha Singh | female | female | 12.269 | 0.992 | ✅ |
| sasian_05 | south_asian | Vikram Reddy | male | male | 12.378 | 0.992 | ✅ |
| sasian_06 | south_asian | Anjali Gupta | female | female | 10.299 | 0.985 | ✅ |
| sasian_07 | south_asian | Imran Khan | male | male | 7.371 | 0.972 | ✅ |
| sasian_08 | south_asian | Fatima Rahman | female | female | 12.079 | 0.991 | ✅ |
| arab_01 | arabic | Mohammed Al-Rashid | male | male | 10.500 | 0.985 | ✅ |
| arab_02 | arabic | Fatima Hassan | female | female | 13.041 | 0.999 | ✅ |
| arab_03 | arabic | Ahmed Ibrahim | male | male | 11.300 | 0.988 | ✅ |
| arab_04 | arabic | Layla Mansour | female | female | 13.256 | 0.994 | ✅ |
| arab_05 | arabic | Yusuf Nasser | male | male | 11.013 | 0.986 | ✅ |
| arab_06 | arabic | Aaliyah Khalil | female | female | 10.900 | 0.986 | ✅ |
| arab_07 | arabic | Omar Saleh | male | male | 11.744 | 0.991 | ✅ |
| arab_08 | arabic | Noor Hamdan | female | female | 1.349 | 0.967 | ✅ |
| slavic_01 | slavic | Ivan Petrov | male | male | 14.552 | 0.998 | ✅ |
| slavic_02 | slavic | Anna Sokolova | female | female | 16.592 | 1.000 | ✅ |
| slavic_03 | slavic | Pavel Novak | male | male | 13.329 | 0.995 | ✅ |
| slavic_04 | slavic | Olga Volkova | female | female | 14.013 | 0.997 | ✅ |
| slavic_05 | slavic | Andrzej Kowalski | male | male | 12.212 | 0.994 | ✅ |
| slavic_06 | slavic | Katarzyna Nowak | female | female | 14.068 | 0.997 | ✅ |
| slavic_07 | slavic | Dmitri Ivanov | male | male | 11.985 | 0.991 | ✅ |
| slavic_08 | slavic | Svetlana Kuznetsova | female | female | 16.350 | 1.000 | ✅ |
| other_01 | other | Carlos Rodriguez | male | male | 10.842 | 0.986 | ✅ |
| other_02 | other | Maria Garcia | female | female | 13.349 | 0.995 | ✅ |
| other_03 | other | Adesola Okonkwo | female | female | 8.134 | 0.972 | ✅ |
| other_04 | other | Kwame Asante | male | male | 6.590 | 0.992 | ✅ |
| other_05 | other | Reza Hosseini | male | male | 5.706 | 0.994 | ✅ |
| other_06 | other | Soraya Karimi | female | female | 12.349 | 0.992 | ✅ |
| other_07 | other | Nguyen Tran | male | male | 3.474 | 0.847 | ✅ |
| other_08 | other | Aroon Suksawat | male | male | 9.418 | 0.983 | ✅ |

## Notes

- **Score** is NamSor's raw confidence; **probabilityCalibrated** is the calibrated [0, 1] probability the prediction is correct (per NamSor's calibration set).
- The 'expected' column is a sanity-check ground truth based on common usage — *not* claimed authoritative. Some names are genuinely ambiguous (e.g., gender-balanced first names within a region).
- For Stage 1 production, NamSor is locked as the escalation for the low-confidence subset that gender_guesser + Genderize won't commit on (per `phase-0.2-plan.md` §4).

## Acceptance check (Wave 1B)

- API key in env (NAMSOR_API_KEY): ✅ (load_dotenv from .env)
- 50-name response cached: ✅ (`namsor-smoke-response.json`)
- Per-region accuracy table logged: ✅ (above)

## Artifacts

- `experiments/phase-0.2/namsor-smoke.md` — this artifact
- `experiments/phase-0.2/namsor-smoke-response.json` — full API response cache
- `experiments/phase-0.2/namsor_smoke.py` — this script
