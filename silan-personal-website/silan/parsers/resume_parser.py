"""
Resume parser for extracting structured personal information, education,
experience, publications, and other resume-related data.
"""

from __future__ import annotations
import re
from typing import Dict, Any, List, Optional
from datetime import datetime, date
from .base_parser import BaseParser, ExtractedContent


class ResumeParser(BaseParser):
    """
    Specialized parser for resume/CV content.

    Extracts personal information, education, work experience, publications,
    awards, skills, research, and recent updates with high accuracy.
    """

    # ===== Precompiled regexes (fewer runtime allocations) =====
    _RE_QUOTED_TITLE = re.compile(r'"([^"]+)"')
    _RE_YEAR_PARENS = re.compile(r'\((\d{4})\)')
    _RE_DOI = re.compile(r'doi:?\s*([^\s]+)', re.IGNORECASE)
    _RE_PUB_NUMBERED = re.compile(r'(\d+)\.\s+(.+?)(?=\n\d+\.|$)', re.DOTALL)
    _RE_GPA = re.compile(r'GPA:?\s*(\d+\.?\d*(?:/\d+\.?\d*)?)', re.IGNORECASE)
    _RE_GPA_FALLBACK = re.compile(r'(\d+\.?\d*/\d+\.?\d*)')
    _RE_AWARD_MONTH_YEAR = re.compile(r'(\w+\s+\d{4})')
    _RE_SOCIAL_USER = [
        re.compile(r'github\.com/([^/]+)', re.I),
        re.compile(r'linkedin\.com/in/([^/]+)', re.I),
        re.compile(r'twitter\.com/([^/]+)', re.I),
        re.compile(r'instagram\.com/([^/]+)', re.I),
        re.compile(r'facebook\.com/([^/]+)', re.I),
    ]

    def __init__(self, content_dir):
        super().__init__(content_dir, logger_name="resume_parser")

    def _get_content_type(self) -> str:
        return "resume"

    # ===== Top-level parse =====
    def _parse_content(self, post, extracted: ExtractedContent) -> None:
        metadata: Dict[str, Any] = post.metadata or {}
        content: str = post.content or ""

        resume_config = metadata.get("resume_config", {}) or {}
        file_info = metadata.get("file_info", {}) or {}
        language = metadata.get("language", "") or ""

        personal = self._extract_personal_info(metadata, content, resume_config, file_info)
        extracted.main_entity = personal

        social = self._extract_social_links(metadata)
        edu = self._enhance_education_with_metadata(self._extract_education(content), metadata)
        exp = self._enhance_experience_with_metadata(self._extract_work_experience(content), metadata)
        pubs = self._extract_publications(content)
        awards = self._extract_awards(content)
        skills = self._extract_skills(content)
        techs = self._parse_technologies(skills.get("technologies", []))
        research = self._extract_research_experience(content)
        updates = self._extract_recent_updates(content)

        personal.update({
            "social_links": social,
            "education": edu,
            "experience": exp,
            "publications": pubs,
            "awards": awards,
            "skills": skills,
            "research": research,
            "recent_updates": updates,
        })

        extracted.metadata.update({
            "title": personal.get("title", ""),
            "current_status": personal.get("current_status", ""),
            "social_links": social,
            "education": edu,
            "experience": exp,
            "publications": pubs,
            "awards": awards,
            "skills": skills,
            "research": research,
            "recent_updates": updates,
            "resume_config": resume_config,
            "file_info": file_info,
            "language": language,
            "frontmatter": metadata,  # Preserve original frontmatter
        })
        extracted.technologies = techs

    # ===== Personal info =====
    def _extract_personal_info(
        self,
        metadata: Dict[str, Any],
        content: str,
        resume_config: Dict | None = None,
        file_info: Dict | None = None,
    ) -> Dict[str, Any]:
        resume_config = resume_config or {}
        file_info = file_info or {}

        title = self._extract_professional_title(content) or metadata.get("title", "")

        info = {
            "full_name": metadata.get("name", "") or "",
            "title": title,
            "current_status": metadata.get("current", "") or "",
            "phone": metadata.get("phone", "") or "",
            "email": metadata.get("email", "") or "",
            "location": metadata.get("location", "") or "",
            "website": metadata.get("website", "") or "",
            "linkedin_url": metadata.get("linkedin", "") or "",
            "github_url": metadata.get("github", "") or "",
            "avatar_url": self._extract_avatar_url(metadata, content),
            "is_primary": bool(file_info.get("is_primary", True)),
            "language": file_info.get("language", "") or "",
            "language_name": file_info.get("language_name", "") or "",
            "sort_order": int(file_info.get("sort_order", 0)),
        }

        for c in metadata.get("contacts", []) or []:
            ctype = (c.get("type") or "").lower()
            val = c.get("value") or ""
            if ctype == "email" and not info["email"]:
                info["email"] = val
            elif ctype == "phone" and not info["phone"]:
                info["phone"] = val
            elif ctype == "location" and not info["location"]:
                info["location"] = val

        return info

    def _extract_social_links(self, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        links = metadata.get("socialLinks") or []
        return [{
            "platform": l.get("type", "") or "",
            "url": l.get("url", "") or "",
            "display_name": l.get("display_name") or self._extract_username_from_url(l.get("url", "") or ""),
            "is_active": True,
            "sort_order": i,
        } for i, l in enumerate(links)]

    def _extract_avatar_url(self, metadata: Dict[str, Any], content: str) -> str:
        for k in ("avatar_url", "avatar", "photo", "profile_photo", "image"):
            if metadata.get(k):
                return metadata[k]
        imgs = self._extract_images(content) or []
        for img in imgs:
            alt = (img.get("alt_text") or "").lower()
            url = img.get("image_url") or ""
            if any(x in alt for x in ("profile", "avatar", "photo", "headshot")) and url:
                return url
        return (imgs[0].get("image_url") if imgs else "") or ""

    def _extract_professional_title(self, content: str) -> str:
        # Prefer frontmatter-like line if present
        for line in content.splitlines():
            if line.startswith("title:"):
                return line.split(":", 1)[1].strip()
        return "AI Researcher"

    # ===== Education =====
    def _extract_education(self, content: str) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        for i, lines in enumerate(self._iterate_section_blocks(content, "Education", heading_level=3)):
            rec = self._parse_education_entry(lines, sort_order=i)
            if rec:
                items.append(rec)
        return items

    def _parse_education_entry(self, lines: List[str], *, sort_order: int = 0) -> Optional[Dict[str, Any]]:
        if not lines:
            return None
        institution = lines[0].lstrip("#").strip()
        rec = {
            "institution": institution,
            "degree": "",
            "field_of_study": "",
            "start_date": None,
            "end_date": None,
            "is_current": False,
            "gpa": None,
            "location": "",
            "institution_website": "",
            "institution_logo_url": "",
            "sort_order": sort_order,
        }
        details: List[str] = []

        for raw in lines[1:]:
            line = raw.strip()
            if not line:
                continue

            if line.startswith("*Logo*:"):
                rec["_logo_key"] = line.replace("*Logo*:", "", 1).strip()
                continue
            if line.startswith("*Website*:"):
                rec["institution_website"] = line.replace("*Website*:", "", 1).strip()
                continue
            if line.startswith("**") and line.endswith("**"):
                degree_text = line.strip("*").strip()
                rec["degree"] = degree_text
                m = re.search(r"\(([^)]+)\)", degree_text)
                if m:
                    rec["field_of_study"] = m.group(1).strip()
                continue
            if line.startswith("*") and not line.startswith("**"):
                info = line.strip("*").strip()
                if any(y in info for y in ("20", "19", "Future")):
                    s, e = self._parse_date_range(info)
                    rec["start_date"], rec["end_date"] = s, e
                    rec["is_current"] = "Future" in info or e is None
                else:
                    rec["location"] = info
                continue
            if "gpa" in line.lower():
                m = self._RE_GPA.search(line) or self._RE_GPA_FALLBACK.search(line)
                if m:
                    rec["gpa"] = m.group(1)
                continue
            if line.startswith("- "):
                details.append(line[2:].strip())
            elif not line.startswith("#"):
                details.append(line)

        rec["details"] = [d for d in (s.strip() for s in details) if d]
        return rec

    def _enhance_education_with_metadata(self, data: List[Dict], metadata: Dict) -> List[Dict]:
        logos = metadata.get("education_logos", {}) or {}
        sites = metadata.get("education_websites", {}) or {}
        for edu in data:
            if "_logo_key" in edu:
                key = edu.pop("_logo_key")
                if key in logos:
                    edu["institution_logo_url"] = logos[key]
            else:
                inst = (edu.get("institution") or "").lower()
                edu["institution_logo_url"] = self._auto_match(logos, inst) or edu.get("institution_logo_url", "")

            if not edu.get("institution_website"):
                inst = (edu.get("institution") or "").lower()
                edu["institution_website"] = self._auto_match(sites, inst) or ""
        return data

    # ===== Experience =====
    def _extract_work_experience(self, content: str) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        for i, lines in enumerate(self._iterate_section_blocks(content, "Work Experience", heading_level=3)):
            rec = self._parse_experience_entry(lines, sort_order=i)
            if rec:
                items.append(rec)
        return items

    def _parse_experience_entry(self, lines: List[str], *, sort_order: int = 0) -> Optional[Dict[str, Any]]:
        if not lines:
            return None
        company = lines[0].lstrip("#").strip()
        rec = {
            "company": company,
            "position": "",
            "start_date": None,
            "end_date": None,
            "is_current": False,
            "location": "",
            "company_website": "",
            "company_logo_url": "",
            "sort_order": sort_order,
        }
        details: List[str] = []

        for raw in lines[1:]:
            line = raw.strip()
            if not line:
                continue

            if line.startswith("*Logo*:"):
                rec["_logo_key"] = line.replace("*Logo*:", "", 1).strip()
                continue
            if line.startswith("*Website*:"):
                rec["company_website"] = line.replace("*Website*:", "", 1).strip()
                continue
            if line.startswith("**") and line.endswith("**"):
                rec["position"] = line.strip("*").strip()
                continue
            if line.startswith("*") and not line.startswith("**"):
                info = line.strip("*").strip()
                if any(y in info for y in ("20", "19", "Now")):
                    s, e = self._parse_date_range(info)
                    rec["start_date"], rec["end_date"] = s, e
                    rec["is_current"] = "Now" in info or e is None
                else:
                    rec["location"] = info
                continue
            if line.startswith("- "):
                details.append(line[2:].strip())
            elif not line.startswith("#"):
                details.append(line)

        rec["details"] = [d for d in (s.strip() for s in details) if d]
        return rec

    def _enhance_experience_with_metadata(self, data: List[Dict], metadata: Dict) -> List[Dict]:
        logos = metadata.get("experience_logos", {}) or {}
        sites = metadata.get("experience_websites", {}) or {}
        for exp in data:
            if "_logo_key" in exp:
                key = exp.pop("_logo_key")
                if key in logos:
                    exp["company_logo_url"] = logos[key]
            else:
                txt = f"{(exp.get('company') or '').lower()} {' '.join(exp.get('details', [])).lower()}"
                exp["company_logo_url"] = self._auto_match(logos, txt) or exp.get("company_logo_url", "")

            if not exp.get("company_website"):
                txt = f"{(exp.get('company') or '').lower()} {' '.join(exp.get('details', [])).lower()}"
                exp["company_website"] = self._auto_match(sites, txt) or ""
        return data

    # ===== Publications =====
    def _extract_publications(self, content: str) -> List[Dict[str, Any]]:
        section = self._extract_section(content, "Publications")
        if not section:
            return []
        pubs: List[Dict[str, Any]] = []
        for m in self._RE_PUB_NUMBERED.finditer(section):
            rec = self._parse_publication_entry(m.group(2).strip())
            if rec:
                pubs.append(rec)
        return pubs

    def _parse_publication_entry(self, text: str) -> Optional[Dict[str, Any]]:
        title = ""
        qm = self._RE_QUOTED_TITLE.search(text)
        if qm:
            title = qm.group(1).strip()
        else:
            # crude but reliable fallback: strip authors then take first sentence-ish
            no_auth = self._strip_author_prefix(text)
            title = (no_auth.split(".")[0] if "." in no_auth else no_auth).strip()
        if len(title) < 3:
            title = "Publication title needs manual review"

        ym = self._RE_YEAR_PARENS.search(text)
        year = int(ym.group(1)) if ym else None

        journal = self._first_match(
            text,
            [
                r'In\s+([^,.(]+)',
                r'Proceedings of\s+([^,.(]+)',
                r'Journal of\s+([^,.(]+)',
                r'([A-Z][^,.(]*(?:Conference|Workshop|Symposium|Journal)[^,.(]*)',
            ],
            flags=re.I,
        ) or ""

        doi = self._RE_DOI.search(text)
        authors = self._extract_authors(text)

        return {
            "title": title,
            "authors": authors,
            "journal_name": journal,
            "publication_type": self._determine_publication_type(text),
            "publication_date": date(year, 1, 1) if year else None,
            "doi": doi.group(1) if doi else "",
            "is_peer_reviewed": True,
            "sort_order": 0,
        }

    def _strip_author_prefix(self, text: str) -> str:
        # Remove leading numbering and obvious author prefix up to first quoted title or venue keyword
        t = re.sub(r'^\d+\.\s*', '', text).strip()
        t = re.sub(r'^[^"]+?"', '"', t)  # if there was a quoted title, keep it
        t = re.sub(r'^[^."]+?(?=\s+(In|Proceedings|Journal|\(\d{4}\)))', '', t, flags=re.I)
        return t.strip().lstrip(",. ").strip()

    def _extract_authors(self, text: str) -> List[str]:
        # Grab prefix until common cut markers, then split on ' and ', '&', or commas
        t = re.sub(r'^\d+\.\s*', '', text).strip()
        cut = re.split(r'("\s*| In\s| Proceedings| Journal| \(\d{4}\))', t, maxsplit=1, flags=re.I)
        head = cut[0].strip() if cut else ""
        if not head:
            return []
        if " and " in head:
            parts = [p.strip() for p in head.split(" and ")]
        elif " & " in head:
            parts = [p.strip() for p in head.split(" & ")]
        elif ", " in head and "." not in head.split(",")[0]:
            parts = [p.strip() for p in head.split(",")]
        else:
            parts = [head]
        out = []
        for p in parts:
            p = re.sub(r'[,;.\s]+$', '', p).strip()
            if p and 2 <= len(p) <= 80 and not p.isdigit():
                out.append(p)
        return out

    def _determine_publication_type(self, text: str) -> str:
        tl = text.lower()
        if "conference" in tl or "proceedings" in tl:
            return "conference"
        if "journal" in tl or "transactions" in tl:
            return "journal"
        if "workshop" in tl:
            return "workshop"
        if "arxiv" in tl or "preprint" in tl:
            return "preprint"
        return "journal"

    # ===== Awards =====
    def _extract_awards(self, content: str) -> List[Dict[str, Any]]:
        section = self._extract_section(content, "Awards")
        if not section:
            return []
        awards: List[Dict[str, Any]] = []
        for line in section.splitlines():
            line = line.strip()
            if line.startswith("- "):
                rec = self._parse_award_entry(line[2:].strip())
                if rec:
                    awards.append(rec)
        return awards

    def _parse_award_entry(self, text: str) -> Optional[Dict[str, Any]]:
        dm = self._RE_AWARD_MONTH_YEAR.search(text)
        award_date = self._parse_month_year(dm.group(1)) if dm else None

        title = re.sub(r'^\w+\s+\d{4}\s+', '', text).strip()
        om = re.search(r'by\s+([^,]+)', title)
        org = (om.group(1).strip() if om else "")
        if om:
            title = title.replace(om.group(0), "").strip()

        return {
            "title": title,
            "awarding_organization": org,
            "award_date": award_date,
            "description": text,
            "certificate_url": "",
            "sort_order": 0,
        }

    def _parse_month_year(self, s: str) -> Optional[date]:
        for fmt in ("%b %Y", "%B %Y"):
            try:
                return datetime.strptime(s, fmt).date()
            except ValueError:
                continue
        return None

    # ===== Skills =====
    def _extract_skills(self, content: str) -> Dict[str, Any]:
        section = self._extract_section(content, "Skills")
        if not section:
            return {"technologies": [], "programming_languages": [], "frameworks": [], "tools": [], "soft_skills": []}

        cats = {"technologies": [], "programming_languages": [], "frameworks": [], "tools": [], "soft_skills": []}
        for raw in section.splitlines():
            if ":" not in raw:
                continue
            head, tail = raw.split(":", 1)
            cat = head.strip("- *").lower()
            items = [t.strip() for t in tail.split(",") if t.strip()]
            if "programming" in cat or "language" in cat:
                cats["programming_languages"].extend(items)
            elif "framework" in cat or "technolog" in cat:
                cats["frameworks"].extend(items)
            elif "tool" in cat:
                cats["tools"].extend(items)
            elif "soft" in cat:
                cats["soft_skills"].extend(items)
            else:
                cats["technologies"].extend(items)

        all_techs = cats["programming_languages"] + cats["frameworks"] + cats["tools"] + cats["technologies"]
        cats["technologies"] = sorted(set(all_techs))
        return cats

    # ===== Research =====
    def _extract_research_experience(self, content: str) -> List[Dict[str, Any]]:
        section = self._extract_section(content, "Research Experience")
        if not section:
            return []
        items: List[Dict[str, Any]] = []
        for entry in re.split(r"\n###\s+", section):
            entry = entry.strip()
            if not entry:
                continue
            rec = self._parse_research_entry(entry)
            if rec:
                items.append(rec)
        return items

    def _parse_research_entry(self, entry: str) -> Optional[Dict[str, Any]]:
        lines = [l.strip() for l in entry.splitlines() if l.strip()]
        if not lines:
            return None
        title = lines[0].strip("#").strip()
        rec = {
            "title": title,
            "start_date": None,
            "end_date": None,
            "is_ongoing": False,
            "location": "",
            "research_type": "individual",
            "funding_source": "",
            "funding_amount": None,
            "sort_order": 0,
        }
        desc: List[str] = []
        for line in lines[1:]:
            if line.startswith("*") and not line.startswith("**"):
                info = line.strip("*").strip()
                if any(y in info for y in ("20", "19")):
                    s, e = self._parse_date_range(info)
                    rec["start_date"], rec["end_date"] = s, e
                    rec["is_ongoing"] = e is None
                else:
                    rec["location"] = info
            else:
                desc.append(line)
        txt = "\n".join(desc).strip()
        rec["details"] = [txt] if txt else []
        return rec

    # ===== Recent updates =====
    def _extract_recent_updates(self, content: str) -> List[Dict[str, Any]]:
        section = self._extract_section(content, "Recent Updates")
        if not section:
            return []
        items: List[Dict[str, Any]] = []
        for entry in re.split(r"\n###\s+", section):
            entry = entry.strip()
            if not entry:
                continue
            rec = self._parse_recent_update_entry(entry)
            if rec:
                items.append(rec)
        return items

    def _parse_recent_update_entry(self, entry: str) -> Optional[Dict[str, Any]]:
        lines = [l.strip() for l in entry.splitlines() if l.strip()]
        if not lines:
            return None
        title_line = lines[0].strip("#").strip()
        rec = {
            "id": "",
            "type": "",
            "title": title_line.split(":", 1)[1].strip() if ":" in title_line else title_line,
            "description": "",
            "date": "",
            "tags": [],
            "status": "",
            "priority": "",
        }
        desc: List[str] = []
        for line in lines[1:]:
            if line.startswith("*ID*:"):
                rec["id"] = line.replace("*ID*:", "", 1).strip()
            elif line.startswith("*Type*:"):
                rec["type"] = line.replace("*Type*:", "", 1).strip()
            elif line.startswith("*Date*:"):
                rec["date"] = line.replace("*Date*:", "", 1).strip()
            elif line.startswith("*Status*:"):
                rec["status"] = line.replace("*Status*:", "", 1).strip()
            elif line.startswith("*Priority*:"):
                rec["priority"] = line.replace("*Priority*:", "", 1).strip()
            elif line.startswith("*Tags*:"):
                tags_text = line.replace("*Tags*:", "", 1).strip()
                rec["tags"] = [t.strip() for t in tags_text.split(",") if t.strip()]
            else:
                desc.append(line)
        rec["description"] = "\n".join(desc).strip()
        return rec

    # ===== Validation =====
    def _validate_content(self, extracted: ExtractedContent) -> None:
        main = extracted.main_entity or {}
        if not main.get("full_name"):
            extracted.validation_errors.append("Missing full name")
        if not main.get("email"):
            extracted.validation_warnings.append("Missing email address")

        for edu in extracted.metadata.get("education", []) or []:
            s, e = edu.get("start_date"), edu.get("end_date")
            if s and e and s > e:
                extracted.validation_errors.append(f'Invalid date range in education: {edu.get("institution","")}')

        for xp in extracted.metadata.get("experience", []) or []:
            s, e = xp.get("start_date"), xp.get("end_date")
            if s and e and s > e:
                extracted.validation_errors.append(f'Invalid date range in experience: {xp.get("company","")}')

    # ===== Utilities =====
    def _auto_match(self, mapping: Dict[str, str], hay: str) -> str:
        if not mapping or not hay:
            return ""
        hay = hay.lower()
        for key, val in mapping.items():
            k = key.lower()
            if k in hay or any(tok in hay for tok in k.split("_")):
                return val
        return ""

    def _first_match(self, text: str, patterns: List[str], flags: int = 0) -> Optional[str]:
        for p in patterns:
            m = re.search(p, text, flags)
            if m:
                return m.group(1).strip()
        return None

    def _extract_username_from_url(self, url: str) -> str:
        if not url:
            return ""
        for rgx in self._RE_SOCIAL_USER:
            m = rgx.search(url)
            if m:
                return m.group(1)
        return ""
