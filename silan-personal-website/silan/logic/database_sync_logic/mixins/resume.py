"""Resume synchronization helpers."""

from datetime import datetime
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from ....core.exceptions import DatabaseError
from ....models import (
    Award,
    Education,
    EducationDetail,
    PersonalInfo,
    Publication,
    PublicationAuthor,
    ResearchProject,
    ResearchProjectDetail,
    SocialLink,
    WorkExperience,
    WorkExperienceDetail,
)


class ResumeSyncMixin:
    """Resume-related synchronization utilities."""

    def _sync_resume(self, session: Session, content_data: Dict[str, Any], item: Dict[str, Any], content_hash: str = None) -> None:
        """Sync resume to database"""
        try:
            # Handle both structured data and frontmatter-based data
            if 'frontmatter' in content_data:
                frontmatter = content_data.get('frontmatter', {})
                content = content_data.get('content', '')
            else:
                # Direct structured data from parsers
                frontmatter = content_data
                content = content_data.get('content', '')

            # Upsert personal info instead of delete+recreate
            assert self.current_user_id is not None
            existing_pi = session.query(PersonalInfo).filter_by(user_id=self.current_user_id, is_primary=True).first()
            if existing_pi:
                existing_pi.full_name = frontmatter.get('name', frontmatter.get('full_name', existing_pi.full_name or 'Unknown'))
                existing_pi.title = frontmatter.get('title', frontmatter.get('current_position', existing_pi.title or 'Professional'))
                existing_pi.current_status = frontmatter.get('current', frontmatter.get('bio', frontmatter.get('summary', existing_pi.current_status or '')))
                existing_pi.location = frontmatter.get('location', existing_pi.location or '')
                existing_pi.email = frontmatter.get('email', existing_pi.email or '')
                existing_pi.phone = frontmatter.get('phone', existing_pi.phone or '')
                existing_pi.website = frontmatter.get('website', existing_pi.website or '')
                existing_pi.avatar_url = frontmatter.get('profile_image', frontmatter.get('avatar_url', existing_pi.avatar_url or ''))
                personal_info = existing_pi
                self.sync_stats['updated_count'] += 1
            else:
                personal_info = PersonalInfo(
                    user_id=self.current_user_id,
                    full_name=frontmatter.get('name', frontmatter.get('full_name', 'Unknown')),
                    title=frontmatter.get('title', frontmatter.get('current_position', 'Professional')),
                    current_status=frontmatter.get('current', frontmatter.get('bio', frontmatter.get('summary', ''))),
                    location=frontmatter.get('location', ''),
                    email=frontmatter.get('email', ''),
                    phone=frontmatter.get('phone', ''),
                    website=frontmatter.get('website', ''),
                    avatar_url=frontmatter.get('profile_image', frontmatter.get('avatar_url', '')),
                    is_primary=True
                )
                session.add(personal_info)
                session.flush()
                self.sync_stats['created_count'] += 1

            # Upsert education records
            education_data = content_data.get('education', [])
            self._sync_education(session, education_data)

            # Upsert work experience records (also handles details inside)
            experience_data = content_data.get('experience', [])
            self._sync_work_experience(session, experience_data)

            # Upsert awards if present
            awards_data = content_data.get('awards', [])
            if awards_data:
                self._sync_awards(session, awards_data)

            self.debug("Resume sync completed (upsert version)")

        except Exception as e:
            raise DatabaseError(f"Failed to sync resume: {e}")

    def _delete_all_resume_records(self, session: Session) -> None:
        """Delete all resume-related records for clean recreation using SQL"""
        try:
            # 使用原生SQL避免UUID对象问题
            from sqlalchemy import text

            # 按外键依赖顺序删除：子表 -> 父表
            # 删除所有resume相关表的所有记录（简单粗暴）
            session.execute(text("DELETE FROM education_details"))
            session.execute(text("DELETE FROM work_experience_details"))
            session.execute(text("DELETE FROM publication_authors"))
            session.execute(text("DELETE FROM research_project_details"))
            session.execute(text("DELETE FROM education"))
            session.execute(text("DELETE FROM work_experience"))
            session.execute(text("DELETE FROM awards"))
            session.execute(text("DELETE FROM publications"))
            session.execute(text("DELETE FROM research_projects"))
            session.execute(text("DELETE FROM social_links"))
            session.execute(text("DELETE FROM personal_info"))

            session.flush()
            self.debug("Successfully deleted all existing resume records using SQL")

        except Exception as e:
            self.warning(f"Failed to delete resume records: {e}")

    def _sync_education(self, session: Session, education_data: List[Dict[str, Any]]) -> None:
        """Sync education data to database"""
        for edu_item in education_data:
            # Check if education record exists
            existing_education = session.query(Education).filter_by(
                user_id=self.current_user_id,
                institution=edu_item.get('institution', ''),
                degree=edu_item.get('degree', '')
            ).first()

            if existing_education:
                # Update existing education
                existing_education.field_of_study = edu_item.get('field_of_study', '')
                existing_education.start_date = self._parse_date(edu_item.get('start_date'))
                existing_education.end_date = self._parse_date(edu_item.get('end_date'))
                existing_education.is_current = edu_item.get('is_current', False)
                existing_education.gpa = edu_item.get('gpa')
                existing_education.location = edu_item.get('location', '')
                existing_education.institution_website = edu_item.get('institution_website', '')
                existing_education.institution_logo_url = edu_item.get('institution_logo_url', '')
                existing_education.updated_at = datetime.utcnow()

                education = existing_education
                self.sync_stats['updated_count'] += 1
            else:
                # Create new education record
                education = Education(
                    user_id=self.current_user_id,
                    institution=edu_item.get('institution', ''),
                    degree=edu_item.get('degree', ''),
                    field_of_study=edu_item.get('field_of_study', ''),
                    start_date=self._parse_date(edu_item.get('start_date')),
                    end_date=self._parse_date(edu_item.get('end_date')),
                    is_current=edu_item.get('is_current', False),
                    gpa=edu_item.get('gpa'),
                    location=edu_item.get('location', ''),
                    institution_website=edu_item.get('institution_website', ''),
                    institution_logo_url=edu_item.get('institution_logo_url', ''),
                    sort_order=len(session.query(Education).filter_by(user_id=self.current_user_id).all())
                )
                session.add(education)
                session.flush()  # Get the ID for foreign key relationships
                session.refresh(education)  # Refresh to ensure UUID is properly loaded
                self.sync_stats['created_count'] += 1

            # Sync education details if present
            details = edu_item.get('details', [])
            if details:
                session.flush()
                session.refresh(education)
                # Now sync education details
                self._sync_education_details(session, education, details)

    def _sync_work_experience(self, session: Session, experience_data: List[Dict[str, Any]]) -> None:
        """Sync work experience data to database"""
        for exp_item in experience_data:
            # Check if work experience record exists
            existing_experience = session.query(WorkExperience).filter_by(
                user_id=self.current_user_id,
                company=exp_item.get('company', ''),
                position=exp_item.get('position', '')
            ).first()

            if existing_experience:
                # Update existing experience
                existing_experience.start_date = self._parse_date(exp_item.get('start_date'))
                existing_experience.end_date = self._parse_date(exp_item.get('end_date'))
                existing_experience.is_current = exp_item.get('is_current', False)
                existing_experience.location = exp_item.get('location', '')
                existing_experience.company_website = exp_item.get('company_website', '')
                existing_experience.company_logo_url = exp_item.get('company_logo_url', '')
                existing_experience.updated_at = datetime.utcnow()

                work_experience = existing_experience
                self.sync_stats['updated_count'] += 1
            else:
                # Create new work experience record
                work_experience = WorkExperience(
                    user_id=self.current_user_id,
                    company=exp_item.get('company', ''),
                    position=exp_item.get('position', ''),
                    start_date=self._parse_date(exp_item.get('start_date')),
                    end_date=self._parse_date(exp_item.get('end_date')),
                    is_current=exp_item.get('is_current', False),
                    location=exp_item.get('location', ''),
                    company_website=exp_item.get('company_website', ''),
                    company_logo_url=exp_item.get('company_logo_url', ''),
                    sort_order=len(session.query(WorkExperience).filter_by(user_id=self.current_user_id).all())
                )
                session.add(work_experience)
                session.flush()  # Get the ID for foreign key relationships
                session.refresh(work_experience)  # Refresh to ensure UUID is properly loaded
                self.sync_stats['created_count'] += 1

            # Sync work experience details immediately after creating the record
            details = exp_item.get('details', [])
            if details:
                # Flush instead of commit to keep all inserts in one transaction
                session.flush()
                session.refresh(work_experience)
                # Now sync work experience details
                self._sync_work_experience_details(session, work_experience, details)

    def _sync_awards(self, session: Session, awards_data: List[Dict[str, Any]]) -> None:
        """Sync awards data to database"""
        for award_item in awards_data:
            # Check if award record exists
            existing_award = session.query(Award).filter_by(
                user_id=self.current_user_id,
                title=award_item.get('title', ''),
                awarding_organization=award_item.get('awarding_organization', award_item.get('issuer', ''))
            ).first()

            if existing_award:
                # Update existing award
                existing_award.award_date = self._parse_date(award_item.get('award_date'))
                existing_award.description = award_item.get('description', '')
                existing_award.updated_at = datetime.utcnow()
                self.sync_stats['updated_count'] += 1
            else:
                # Create new award record
                award = Award(
                    user_id=self.current_user_id,
                    title=award_item.get('title', ''),
                    awarding_organization=award_item.get('awarding_organization', award_item.get('issuer', '')),
                    award_date=self._parse_date(award_item.get('award_date')),
                    description=award_item.get('description', ''),
                    sort_order=len(session.query(Award).filter_by(user_id=self.current_user_id).all())
                )
                session.add(award)
                self.sync_stats['created_count'] += 1

    def _sync_education_details(self, session: Session, education: Education, details: List[str]) -> None:
        """Sync education details to database"""

        # Check if details already exist
        existing_count = session.query(EducationDetail).filter(
            EducationDetail.education_id == education.id
        ).count()

        if existing_count > 0:
            return

        # Create new details
        for i, detail_text in enumerate(details):
            if not detail_text or not detail_text.strip():
                continue

            try:
                education_detail = EducationDetail(
                    education_id=education.id,
                    detail_text=detail_text.strip(),
                    sort_order=i
                )
                session.add(education_detail)
                # Force individual insert to avoid insertmanyvalues bulk processing
                session.flush()
                self.sync_stats['created_count'] += 1
            except Exception as e:
                self.warning(f"Failed to create education detail: {e}")
                continue

    def _sync_work_experience_details(self, session: Session, work_experience: WorkExperience, details: List[str]) -> None:
        """Sync work experience details to database"""

        # Check if details already exist
        existing_count = session.query(WorkExperienceDetail).filter(
            WorkExperienceDetail.work_experience_id == work_experience.id
        ).count()

        if existing_count > 0:
            return

        # Create new details
        for i, detail_text in enumerate(details):
            if not detail_text or not detail_text.strip():
                continue

            try:
                work_experience_detail = WorkExperienceDetail(
                    work_experience_id=work_experience.id,
                    detail_text=detail_text.strip(),
                    sort_order=i
                )
                session.add(work_experience_detail)
                # Force individual insert to avoid insertmanyvalues bulk processing
                session.flush()
                self.sync_stats['created_count'] += 1
            except Exception as e:
                self.warning(f"Failed to create work experience detail: {e}")
                continue

    def _sync_publications(self, session: Session, publications_data: List[Dict[str, Any]]) -> None:
        """Sync publications data to database"""
        for pub_item in publications_data:
            # Check if publication record exists
            existing_publication = session.query(Publication).filter_by(
                user_id=self.current_user_id,
                title=pub_item.get('title', '')
            ).first()

            if existing_publication:
                # Update existing publication
                existing_publication.publication_type = pub_item.get('publication_type', 'journal')
                existing_publication.journal_name = pub_item.get('journal_name', '')
                existing_publication.publication_date = pub_item.get('publication_date')
                existing_publication.doi = pub_item.get('doi', '')
                existing_publication.is_peer_reviewed = pub_item.get('is_peer_reviewed', True)
                existing_publication.updated_at = datetime.utcnow()

                publication = existing_publication
                self.sync_stats['updated_count'] += 1
            else:
                # Create new publication record
                publication = Publication(
                    user_id=self.current_user_id,
                    title=pub_item.get('title', ''),
                    publication_type=pub_item.get('publication_type', 'journal'),
                    journal_name=pub_item.get('journal_name', ''),
                    publication_date=pub_item.get('publication_date'),
                    doi=pub_item.get('doi', ''),
                    is_peer_reviewed=pub_item.get('is_peer_reviewed', True),
                    sort_order=len(session.query(Publication).filter_by(user_id=self.current_user_id).all())
                )
                session.add(publication)
                session.flush()
                session.refresh(publication)  # Refresh to ensure UUID is properly loaded
                self.sync_stats['created_count'] += 1

            # Check if publication authors already exist for this publication
            existing_authors_count = session.query(PublicationAuthor).filter_by(
                publication_id=publication.id
            ).count()

            if existing_authors_count > 0:
                continue

            # Sync publication authors
            authors = pub_item.get('authors', [])
            for i, author in enumerate(authors):
                # Handle both string and dict format for authors
                if isinstance(author, str):
                    author_name = author
                    is_corresponding = False
                    affiliation = ''
                else:
                    author_name = author.get('name', '')
                    is_corresponding = author.get('is_corresponding', False)
                    affiliation = author.get('affiliation', '')

                publication_author = PublicationAuthor(
                    publication_id=publication.id,
                    author_name=author_name,
                    author_order=i,
                    is_corresponding=is_corresponding,
                    affiliation=affiliation
                )
                session.add(publication_author)
                self.sync_stats['created_count'] += 1

    def _sync_publication_authors(self, session: Session, publication: Publication, authors: List[str]) -> None:
        """Sync publication authors for a publication"""
        # Check if authors already exist to avoid duplicates
        try:
            existing_count = session.query(PublicationAuthor).filter(
                PublicationAuthor.publication_id == str(publication.id)
            ).count()
            if existing_count > 0:
                self.debug(f"Publication authors already exist for publication {publication.id}, skipping")
                return
        except Exception as e:
            self.warning(f"Error checking existing publication authors, proceeding: {e}")

        for i, author_name in enumerate(authors):
            if not author_name or not author_name.strip():
                continue

            # Create author record
            author = PublicationAuthor(
                publication_id=publication.id,
                author_name=author_name.strip(),
                author_order=i + 1,
                is_corresponding=False  # Could be enhanced to detect corresponding author
            )
            session.add(author)

    def _sync_research_projects(self, session: Session, research_data: List[Dict[str, Any]]) -> None:
        """Sync research projects data to database"""
        for research_item in research_data:
            # Check if research project record exists
            existing_research = session.query(ResearchProject).filter_by(
                user_id=self.current_user_id,
                title=research_item.get('title', research_item.get('institution', ''))
            ).first()

            if existing_research:
                # Update existing research project
                existing_research.start_date = self._parse_date(research_item.get('start_date'))
                existing_research.end_date = self._parse_date(research_item.get('end_date'))
                existing_research.is_ongoing = research_item.get('is_current', False)
                existing_research.location = research_item.get('location', '')
                existing_research.research_type = research_item.get('position', research_item.get('research_area', ''))
                existing_research.funding_source = research_item.get('funding_source', '')
                existing_research.updated_at = datetime.utcnow()

                research_project = existing_research
                self.sync_stats['updated_count'] += 1
            else:
                # Create new research project record
                research_project = ResearchProject(
                    user_id=self.current_user_id,
                    title=research_item.get('title', research_item.get('institution', 'Research Project')),
                    start_date=self._parse_date(research_item.get('start_date')),
                    end_date=self._parse_date(research_item.get('end_date')),
                    is_ongoing=research_item.get('is_current', False),
                    location=research_item.get('location', ''),
                    research_type=research_item.get('position', research_item.get('research_area', '')),
                    funding_source=research_item.get('funding_source', ''),
                    sort_order=len(session.query(ResearchProject).filter_by(user_id=self.current_user_id).all())
                )
                session.add(research_project)
                session.flush()  # Get the ID for foreign key relationships
                session.refresh(research_project)  # Refresh to ensure UUID is properly loaded
                self.sync_stats['created_count'] += 1

            # Sync research project details if present
            details = research_item.get('details', [])
            if details:
                session.flush()
                session.refresh(research_project)
                # Now sync research project details
                self._sync_research_project_details(session, research_project, details)

    def _sync_research_project_details(self, session: Session, research_project: ResearchProject, details: List[str]) -> None:
        """Sync research project details to database"""

        # Check if details already exist
        existing_count = session.query(ResearchProjectDetail).filter(
            ResearchProjectDetail.research_project_id == research_project.id
        ).count()

        if existing_count > 0:
            return

        # Create research project details
        for i, detail_text in enumerate(details):
            if not detail_text or not detail_text.strip():
                continue

            try:
                research_project_detail = ResearchProjectDetail(
                    research_project_id=research_project.id,
                    detail_text=detail_text.strip(),
                    sort_order=i
                )
                session.add(research_project_detail)
                # Force individual insert to avoid insertmanyvalues bulk processing
                session.flush()
                self.sync_stats['created_count'] += 1
            except Exception as e:
                self.warning(f"Failed to create research project detail: {e}")
                continue

    def _sync_social_links(self, session: Session, personal_info: PersonalInfo, social_links_data: List[Dict[str, Any]]) -> None:
        """Sync social links data to database"""
        # Check if social links already exist for this personal info
        existing_links_count = session.query(SocialLink).filter_by(
            personal_info_id=personal_info.id
        ).count()

        if existing_links_count > 0:
            return

        # Create new social links
        for i, link_data in enumerate(social_links_data):
            social_link = SocialLink(
                personal_info_id=personal_info.id,
                platform=link_data.get('platform', ''),
                url=link_data.get('url', ''),
                display_name=link_data.get('display_name', ''),
                is_active=link_data.get('is_active', True),
                sort_order=i
            )
            session.add(social_link)
            self.sync_stats['created_count'] += 1

    def _sync_education_with_cleanup(self, session: Session, education_data: List[Dict[str, Any]]) -> None:
        """Sync education data with cleanup - replace all existing records"""
        try:
            # First, delete all existing education records for this user
            existing_educations = session.query(Education).filter_by(user_id=self.current_user_id).all()
            deleted_count = 0

            for education in existing_educations:
                # Delete related education details first using individual queries
                education_details = session.query(EducationDetail).filter(
                    EducationDetail.education_id == education.id
                ).all()
                for detail in education_details:
                    session.delete(detail)
                session.delete(education)
                deleted_count += 1

            if deleted_count > 0:
                session.flush()  # Flush deletions before creating new records
                self.debug(f"Cleaned up {deleted_count} existing education records")

            # Then, create all new education records from the file
            for i, edu_item in enumerate(education_data):
                education = Education(
                    user_id=self.current_user_id,
                    institution=edu_item.get('institution', ''),
                    degree=edu_item.get('degree', ''),
                    field_of_study=edu_item.get('field_of_study', ''),
                    start_date=self._parse_date(edu_item.get('start_date')),
                    end_date=self._parse_date(edu_item.get('end_date')),
                    is_current=edu_item.get('is_current', False),
                    gpa=edu_item.get('gpa'),
                    location=edu_item.get('location', ''),
                    institution_website=edu_item.get('institution_website', ''),
                    institution_logo_url=edu_item.get('institution_logo_url', ''),
                    sort_order=i
                )
                session.add(education)
                session.flush()  # Get the ID for foreign key relationships
                session.refresh(education)
                self.sync_stats['created_count'] += 1

                # Sync education details if present
                details = edu_item.get('details', [])
                if details:
                    self._sync_education_details(session, education, details)

        except Exception as e:
            raise DatabaseError(f"Failed to sync education with cleanup: {e}")

    def _sync_work_experience_with_cleanup(self, session: Session, experience_data: List[Dict[str, Any]]) -> None:
        """Sync work experience data with cleanup - replace all existing records"""
        try:
            # First, delete all existing work experience records for this user
            existing_experiences = session.query(WorkExperience).filter_by(user_id=self.current_user_id).all()
            deleted_count = 0

            for experience in existing_experiences:
                # Delete related work experience details first
                session.query(WorkExperienceDetail).filter(
                    WorkExperienceDetail.work_experience_id == experience.id
                ).delete()
                session.delete(experience)
                deleted_count += 1
            if deleted_count > 0:
                self.debug(f"Cleaned up {deleted_count} existing work experience records")

            # Then, create all new work experience records from the file
            for i, exp_item in enumerate(experience_data):
                work_experience = WorkExperience(
                    user_id=self.current_user_id,
                    company=exp_item.get('company', ''),
                    position=exp_item.get('position', ''),
                    start_date=self._parse_date(exp_item.get('start_date')),
                    end_date=self._parse_date(exp_item.get('end_date')),
                    is_current=exp_item.get('is_current', False),
                    location=exp_item.get('location', ''),
                    company_website=exp_item.get('company_website', ''),
                    company_logo_url=exp_item.get('company_logo_url', ''),
                    sort_order=i
                )
                session.add(work_experience)
                session.flush()  # Get the ID for foreign key relationships
                session.refresh(work_experience)
                self.sync_stats['created_count'] += 1

                # Sync work experience details if present
                details = exp_item.get('details', [])
                if details:
                    self._sync_work_experience_details(session, work_experience, details)

        except Exception as e:
            raise DatabaseError(f"Failed to sync work experience with cleanup: {e}")

    def _sync_awards_with_cleanup(self, session: Session, awards_data: List[Dict[str, Any]]) -> None:
        """Sync awards data with cleanup - replace all existing records"""
        try:
            # First, delete all existing awards for this user
            existing_awards = session.query(Award).filter_by(user_id=self.current_user_id).all()
            deleted_count = len(existing_awards)

            for award in existing_awards:
                session.delete(award)

            if deleted_count > 0:
                self.debug(f"Cleaned up {deleted_count} existing award records")

            # Then, create all new award records from the file
            for i, award_item in enumerate(awards_data):
                award = Award(
                    user_id=self.current_user_id,
                    title=award_item.get('title', ''),
                    awarding_organization=award_item.get('awarding_organization', award_item.get('issuer', '')),
                    award_date=self._parse_date(award_item.get('award_date')),
                    description=award_item.get('description', ''),
                    sort_order=i
                )
                session.add(award)
                self.sync_stats['created_count'] += 1

        except Exception as e:
            raise DatabaseError(f"Failed to sync awards with cleanup: {e}")

    def _sync_publications_with_cleanup(self, session: Session, publications_data: List[Dict[str, Any]]) -> None:
        """Sync publications data with cleanup - replace all existing records"""
        try:
            # Use raw SQL for more reliable deletion with cascading
            session.execute(text("DELETE FROM publication_authors WHERE publication_id IN (SELECT id FROM publications WHERE user_id = :user_id)"),
                          {"user_id": self.current_user_id})
            result = session.execute(text("DELETE FROM publications WHERE user_id = :user_id"),
                                   {"user_id": self.current_user_id})
            deleted_count = result.rowcount

            if deleted_count > 0:
                self.debug(f"Cleaned up {deleted_count} existing publication records")

            # Then, create all new publication records from the file
            for i, pub_item in enumerate(publications_data):
                publication = Publication(
                    user_id=self.current_user_id,
                    title=pub_item.get('title', ''),
                    publication_type=pub_item.get('publication_type', 'journal'),
                    journal_name=pub_item.get('journal_name', ''),
                    publication_date=pub_item.get('publication_date'),
                    doi=pub_item.get('doi', ''),
                    is_peer_reviewed=pub_item.get('is_peer_reviewed', True),
                    sort_order=i
                )
                session.add(publication)
                session.flush()
                session.refresh(publication)
                self.sync_stats['created_count'] += 1

                # Sync publication authors
                authors = pub_item.get('authors', [])
                for j, author in enumerate(authors):
                    # Handle both string and dict format for authors
                    if isinstance(author, str):
                        author_name = author
                        is_corresponding = False
                        affiliation = ''
                    else:
                        author_name = author.get('name', '')
                        is_corresponding = author.get('is_corresponding', False)
                        affiliation = author.get('affiliation', '')

                    publication_author = PublicationAuthor(
                        publication_id=publication.id,
                        author_name=author_name,
                        author_order=j,
                        is_corresponding=is_corresponding,
                        affiliation=affiliation
                    )
                    session.add(publication_author)
                    self.sync_stats['created_count'] += 1

        except Exception as e:
            raise DatabaseError(f"Failed to sync publications with cleanup: {e}")

    def _sync_research_projects_with_cleanup(self, session: Session, research_data: List[Dict[str, Any]]) -> None:
        """Sync research projects data with cleanup - replace all existing records"""
        try:
            # Use raw SQL for more reliable deletion with cascading
            session.execute(text("DELETE FROM research_project_details WHERE research_project_id IN (SELECT id FROM research_projects WHERE user_id = :user_id)"),
                          {"user_id": self.current_user_id})
            result = session.execute(text("DELETE FROM research_projects WHERE user_id = :user_id"),
                                   {"user_id": self.current_user_id})
            deleted_count = result.rowcount

            if deleted_count > 0:
                self.debug(f"Cleaned up {deleted_count} existing research project records")

            # Then, create all new research project records from the file
            for i, research_item in enumerate(research_data):
                research_project = ResearchProject(
                    user_id=self.current_user_id,
                    title=research_item.get('title', research_item.get('institution', 'Research Project')),
                    start_date=self._parse_date(research_item.get('start_date')),
                    end_date=self._parse_date(research_item.get('end_date')),
                    is_ongoing=research_item.get('is_current', False),
                    location=research_item.get('location', ''),
                    research_type=research_item.get('position', research_item.get('research_area', '')),
                    funding_source=research_item.get('funding_source', ''),
                    sort_order=i
                )
                session.add(research_project)
                session.flush()  # Get the ID for foreign key relationships
                session.refresh(research_project)
                self.sync_stats['created_count'] += 1

                # Sync research project details if present
                details = research_item.get('details', [])
                if details:
                    self._sync_research_project_details(session, research_project, details)

        except Exception as e:
            raise DatabaseError(f"Failed to sync research projects with cleanup: {e}")

    def _sync_social_links_with_cleanup(self, session: Session, personal_info: PersonalInfo, social_links_data: List[Dict[str, Any]]) -> None:
        """Sync social links data with cleanup - replace all existing records"""
        try:
            # First, delete all existing social links for this personal info
            existing_links = session.query(SocialLink).filter_by(personal_info_id=personal_info.id).all()
            deleted_count = len(existing_links)

            for link in existing_links:
                session.delete(link)

            if deleted_count > 0:
                self.debug(f"Cleaned up {deleted_count} existing social link records")

            # Then, create all new social link records from the file
            for i, link_data in enumerate(social_links_data):
                social_link = SocialLink(
                    personal_info_id=personal_info.id,
                    platform=link_data.get('platform', ''),
                    url=link_data.get('url', ''),
                    display_name=link_data.get('display_name', ''),
                    is_active=link_data.get('is_active', True),
                    sort_order=i
                )
                session.add(social_link)
                self.sync_stats['created_count'] += 1

        except Exception as e:
            raise DatabaseError(f"Failed to sync social links with cleanup: {e}")
