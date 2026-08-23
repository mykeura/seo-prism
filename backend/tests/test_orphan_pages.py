"""
Unit tests for orphan_pages module.
"""
import pytest
from modules.orphan_pages import OrphanPagesModule


class TestOrphanPagesModule:
    """Tests for OrphanPagesModule class."""
    
    def test_get_base_url(self):
        """Test extracting base URL."""
        module = OrphanPagesModule(None)
        
        assert module._get_base_url('https://example.com/page') == 'https://example.com'
        assert module._get_base_url('http://localhost:3000/page') == 'http://localhost:3000'
        assert module._get_base_url('https://example.com:8080/page') == 'https://example.com:8080'
    
    def test_is_homepage(self):
        """Test detecting homepage."""
        module = OrphanPagesModule(None)
        
        assert module._is_homepage('https://example.com/', 'https://example.com') is True
        assert module._is_homepage('https://example.com', 'https://example.com') is True
        assert module._is_homepage('https://example.com/index.html', 'https://example.com') is True
        assert module._is_homepage('https://example.com/page', 'https://example.com') is False
    
    def test_analyze_orphan_pages(self, temp_db, sample_scan_id):
        """Test detecting orphan pages."""
        module = OrphanPagesModule(temp_db)
        
        # Add pages to database
        page_id_1 = temp_db.add_page(sample_scan_id, 'https://example.com/', 200, '<html></html>')
        page_id_2 = temp_db.add_page(sample_scan_id, 'https://example.com/page', 200, '<html></html>')
        
        # Add link from homepage to page
        temp_db.add_link(page_id_1, 'https://example.com/page', 'https://example.com/')
        
        crawled_pages = [
            {'url': 'https://example.com/', 'status': 200, 'html': '<html></html>'},
            {'url': 'https://example.com/page', 'status': 200, 'html': '<html></html>'},
            {'url': 'https://example.com/orphan', 'status': 200, 'html': '<html></html>'}
        ]
        
        issues = module.analyze(sample_scan_id, crawled_pages, 'https://example.com')
        
        # Should find the orphan page
        assert len(issues) == 1
        assert issues[0]['issue_type'] == 'orphan_page'
        assert 'orphan' in issues[0]['url']
    
    def test_analyze_no_orphan_pages(self, temp_db, sample_scan_id):
        """Test that pages with incoming links are not orphans."""
        module = OrphanPagesModule(temp_db)
        
        # Add pages to database
        page_id_1 = temp_db.add_page(sample_scan_id, 'https://example.com/', 200, '<html></html>')
        page_id_2 = temp_db.add_page(sample_scan_id, 'https://example.com/page1', 200, '<html></html>')
        page_id_3 = temp_db.add_page(sample_scan_id, 'https://example.com/page2', 200, '<html></html>')
        
        # Add links
        temp_db.add_link(page_id_1, 'https://example.com/page1', 'https://example.com/')
        temp_db.add_link(page_id_1, 'https://example.com/page2', 'https://example.com/')
        
        crawled_pages = [
            {'url': 'https://example.com/', 'status': 200, 'html': '<html></html>'},
            {'url': 'https://example.com/page1', 'status': 200, 'html': '<html></html>'},
            {'url': 'https://example.com/page2', 'status': 200, 'html': '<html></html>'}
        ]
        
        issues = module.analyze(sample_scan_id, crawled_pages, 'https://example.com')
        
        # Should not find any orphan pages
        assert len(issues) == 0
    
    def test_analyze_homepage_not_orphan(self, temp_db, sample_scan_id):
        """Test that homepage is not considered an orphan."""
        module = OrphanPagesModule(temp_db)
        
        crawled_pages = [
            {'url': 'https://example.com/', 'status': 200, 'html': '<html></html>'}
        ]
        
        issues = module.analyze(sample_scan_id, crawled_pages, 'https://example.com')
        
        # Homepage should not be flagged as orphan
        assert len(issues) == 0
    
    def test_analyze_multiple_orphan_pages(self, temp_db, sample_scan_id):
        """Test detecting multiple orphan pages."""
        module = OrphanPagesModule(temp_db)
        
        # Add homepage to database
        page_id_1 = temp_db.add_page(sample_scan_id, 'https://example.com/', 200, '<html></html>')
        
        crawled_pages = [
            {'url': 'https://example.com/', 'status': 200, 'html': '<html></html>'},
            {'url': 'https://example.com/orphan1', 'status': 200, 'html': '<html></html>'},
            {'url': 'https://example.com/orphan2', 'status': 200, 'html': '<html></html>'},
            {'url': 'https://example.com/orphan3', 'status': 200, 'html': '<html></html>'}
        ]
        
        issues = module.analyze(sample_scan_id, crawled_pages, 'https://example.com')
        
        # Should find all orphan pages
        assert len(issues) == 3
        assert all(issue['issue_type'] == 'orphan_page' for issue in issues)
    
    def test_analyze_with_internal_links(self, temp_db, sample_scan_id):
        """Test that pages linked internally are not orphans."""
        module = OrphanPagesModule(temp_db)
        
        # Add pages to database
        page_id_1 = temp_db.add_page(sample_scan_id, 'https://example.com/', 200, '<html></html>')
        page_id_2 = temp_db.add_page(sample_scan_id, 'https://example.com/page1', 200, '<html></html>')
        page_id_3 = temp_db.add_page(sample_scan_id, 'https://example.com/page2', 200, '<html></html>')
        
        # Add internal links
        temp_db.add_link(page_id_1, 'https://example.com/page1', 'https://example.com/')
        temp_db.add_link(page_id_2, 'https://example.com/page2', 'https://example.com/page1')
        
        crawled_pages = [
            {'url': 'https://example.com/', 'status': 200, 'html': '<html></html>'},
            {'url': 'https://example.com/page1', 'status': 200, 'html': '<html></html>'},
            {'url': 'https://example.com/page2', 'status': 200, 'html': '<html></html>'}
        ]
        
        issues = module.analyze(sample_scan_id, crawled_pages, 'https://example.com')
        
        # Should not find any orphan pages
        assert len(issues) == 0
    
    def test_analyze_empty_pages(self, temp_db, sample_scan_id):
        """Test analyzing empty pages list."""
        module = OrphanPagesModule(temp_db)
        
        crawled_pages = []
        issues = module.analyze(sample_scan_id, crawled_pages, 'https://example.com')
        
        assert len(issues) == 0
    
    def test_severity_level(self, temp_db, sample_scan_id):
        """Test that orphan pages have medium severity."""
        module = OrphanPagesModule(temp_db)
        
        crawled_pages = [
            {'url': 'https://example.com/', 'status': 200, 'html': '<html></html>'},
            {'url': 'https://example.com/orphan', 'status': 200, 'html': '<html></html>'}
        ]
        
        issues = module.analyze(sample_scan_id, crawled_pages, 'https://example.com')
        
        if issues:
            assert issues[0]['severity'] == 'medium'
    
    def test_analyze_with_resources(self, temp_db, sample_scan_id):
        """Test that resources are not considered as pages."""
        module = OrphanPagesModule(temp_db)
        
        crawled_pages = [
            {'url': 'https://example.com/', 'status': 200, 'html': '<html></html>'},
            {'url': 'https://example.com/style.css', 'status': 200, 'html': None, 'is_resource': True}
        ]
        
        issues = module.analyze(sample_scan_id, crawled_pages, 'https://example.com')
        
        # Should not flag resources as orphan pages
        assert len(issues) == 0
    
    def test_is_homepage_with_path(self):
        """Test homepage detection with various paths."""
        module = OrphanPagesModule(None)
        
        assert module._is_homepage('https://example.com/', 'https://example.com') is True
        assert module._is_homepage('https://example.com', 'https://example.com') is True
        assert module._is_homepage('https://example.com/index.html', 'https://example.com') is True
        assert module._is_homepage('https://example.com/index.php', 'https://example.com') is False
        assert module._is_homepage('https://example.com/page/', 'https://example.com') is False