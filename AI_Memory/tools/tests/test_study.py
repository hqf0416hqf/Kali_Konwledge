import hashlib
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import study


class StudyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for scope in study.SCOPES:
            (self.root / scope).mkdir()
        self.put('WIKI/Linux.md', '# Linux\n## USB\n使用 lsusb 检查设备\n')
        self.put('RAW/a.md', '# 历史\nLSUSB 记录\n')
        self.put('AI_Profile/Profile.md', '# 画像\n偏好实验\n')
        self.put('AI_Memory/当前教学断点.md', '# 断点\n等待验证\n')
        self.put('AI_Memory/CS/state.md', '# 状态\n## CS-01 Linux\n接触过\n来源：用户\n独立应用尚未验证\n')

    def put(self, path, text):
        p = self.root / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding='utf-8')
        return p

    def test_original_lines_and_scope(self):
        result = study.search(self.root, ['lsusb'], ['WIKI'])
        self.assertEqual(result['total'], 1)
        hit = result['hits'][0]
        lines = (self.root / hit['path']).read_text().splitlines()
        self.assertEqual(hit['text'], '\n'.join(lines[hit['start'] - 1:hit['end']]))
        self.assertEqual(hit['matching_lines'], [3])
        self.assertEqual(hit['heading'], 'USB')
        self.assertEqual(len(study.search(self.root, ['lsusb'], ['WIKI', 'RAW'])['hits']), 2)

    def test_rank_multiple_terms_and_no_match(self):
        self.put('WIKI/other.md', '# 其他\nLinux USB\n')
        hits = study.search(self.root, ['Linux', 'USB'], ['WIKI'])['hits']
        self.assertEqual(hits[0]['path'], 'WIKI/other.md')
        self.assertEqual(study.search(self.root, ['不存在词'], ['WIKI'])['hits'], [])
        with self.assertRaises(ValueError):
            study.search(self.root, [' '], ['WIKI'])

    def test_changed_and_deleted_files_visible_without_stale_index(self):
        p = self.put('WIKI/new.md', '# 新增\nunique\n')
        before = study.search(self.root, ['unique'], ['WIKI'])['hits'][0]['sha256']
        p.write_text('# 改名内容\nunique changed\n')
        self.assertNotEqual(before, study.search(self.root, ['unique'], ['WIKI'])['hits'][0]['sha256'])
        p.unlink()
        self.assertEqual(study.search(self.root, ['unique'], ['WIKI'])['hits'], [])

    def test_wiki_tools_directory_is_searchable(self):
        self.put('WIKI/CS/tools/Linux.md', '# Linux\npwd\n')
        self.put('AI_Memory/tools/README.md', '# 程序说明\npwd\n')
        self.put('AI_Memory/History/old.md', '# 旧状态\npwd\n')
        hits = study.search(self.root, ['pwd'], ['WIKI', 'AI_Memory'])['hits']
        self.assertEqual([h['path'] for h in hits], ['WIKI/CS/tools/Linux.md'])

    def test_symlink_and_invalid_encoding(self):
        outside = self.put('outside.md', '# secret\nlsusb\n')
        (self.root / 'WIKI/escape.md').symlink_to(outside)
        (self.root / 'WIKI/bad.md').write_bytes(b'\xff')
        result = study.search(self.root, ['lsusb'], ['WIKI'])
        self.assertEqual(result['total'], 1)
        self.assertEqual(len(result['warnings']), 2)
        with self.assertRaises(ValueError):
            study.safe_path(self.root, '../escape')

    def test_context_sources_and_budget(self):
        text, warnings = study.context(self.root, 'Linux 学到哪里？', ['Linux', 'lsusb'], 4000)
        self.assertFalse(warnings)
        self.assertLessEqual(len(text), 4000)
        for fragment in ['AI_Profile/Profile.md', '当前教学断点.md', 'CS/state.md',
                         'WIKI/Linux.md', '独立应用尚未验证', 'SHA-256']:
            self.assertIn(fragment, text)

    def test_long_context_and_unmatched_query(self):
        self.put('AI_Profile/Profile.md', '# 画像\n' + '很长的偏好\n' * 1000)
        text, _ = study.context(self.root, '问题', ['不存在'], 2000)
        self.assertLessEqual(len(text), 2000)
        self.assertIn('未找到字面匹配', text)
        with self.assertRaises(ValueError):
            study.context(self.root, '问' * 3000, ['Linux'], 2000)

    def test_preview_apply_conflict_and_archive(self):
        target = self.root / 'AI_Memory/CS/state.md'
        before = target.read_bytes()
        candidate = self.put('candidate.md', '# 状态\n用户撤回原自述，当前尚未验证\n')
        kwargs = dict(root=self.root, relative='AI_Memory/CS/state.md', content_file=candidate,
                      expected=hashlib.sha256(before).hexdigest(), source='测试用户纠正',
                      reason='撤回', evidence_date='2026-10-22')
        self.assertFalse(study.update(**kwargs)['applied'])
        self.assertEqual(before, target.read_bytes())
        result = study.update(**kwargs, apply=True)
        self.assertEqual(target.read_bytes(), candidate.read_bytes())
        self.assertEqual((self.root / result['archive'] / 'before.md').read_bytes(), before)
        with self.assertRaises(ValueError):
            study.update(**kwargs, apply=True)
        # Recovery uses the same reviewed update workflow with current digest.
        kwargs['content_file'] = self.root / result['archive'] / 'before.md'
        kwargs['expected'] = study.digest(target.read_bytes())
        study.update(**kwargs, apply=True)
        self.assertEqual(target.read_bytes(), before)
        self.assertFalse(any('History/' in h['path'] for h in
                             study.search(self.root, ['用户'], ['AI_Memory'])['hits']))

    def test_write_boundaries_and_new_file(self):
        candidate = self.put('candidate.md', '# 新状态\n尚未验证\n')
        for path in ['WIKI/Linux.md', '../evil.md', 'AI_Memory/tools/evil.md',
                     'AI_Memory/History/evil.md', 'AI_Profile/data.json']:
            with self.assertRaises(ValueError):
                study.update(self.root, path, candidate, 'NEW', 'source', 'reason', '2026-10-22', True)
        result = study.update(self.root, 'AI_Memory/CS/new.md', candidate, 'NEW',
                              'source', 'reason', '2026-10-22', True)
        self.assertTrue(result['applied'])

    def test_link_checker(self):
        self.put('AI_Memory/links.md', '# 链接\n[画像](../AI_Profile/Profile.md)\n[坏](missing.md)\n')
        result = study.check(self.root)
        self.assertEqual(result['links'], 2)
        self.assertEqual(len(result['problems']), 1)


if __name__ == '__main__':
    unittest.main()
