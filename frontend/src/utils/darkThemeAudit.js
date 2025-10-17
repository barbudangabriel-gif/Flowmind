/**
 * Dark Theme Audit Tool
 * 
 * Rulează în Console pentru a găsi toate elementele cu clase light mode
 * 
 * Usage:
 * 1. Deschide Console (F12)
 * 2. Copy-paste acest fișier în Console
 * 3. Rulează: runAudit()
 * 4. Copy rezultatul și trimite-l către AI
 */

function runAudit() {
 console.log(' Starting Dark Theme Audit...\n');

 // Patterns to check
 const lightPatterns = [
 'bg-white',
 'bg-gray-50',
 'bg-gray-100',
 'bg-blue-50',
 'bg-green-50',
 'text-gray-900',
 'text-gray-800',
 'text-black',
 'border-gray-100',
 'border-gray-200'
 ];

 const issues = [];
 const summary = {
 total: 0,
 byPattern: {}
 };

 lightPatterns.forEach(pattern => {
 const selector = `[class*="${pattern}"]`;
 const elements = document.querySelectorAll(selector);
 
 if (elements.length > 0) {
 summary.byPattern[pattern] = elements.length;
 summary.total += elements.length;

 elements.forEach((el, idx) => {
 // Get parent context
 const parent = el.parentElement;
 const parentInfo = parent ? `${parent.tagName}.${parent.className.split(' ')[0]}` : 'root';

 // Get position info
 const rect = el.getBoundingClientRect();
 const visible = rect.width > 0 && rect.height > 0;

 issues.push({
 pattern,
 tag: el.tagName.toLowerCase(),
 id: el.id || '-',
 classes: el.className,
 text: el.innerText?.substring(0, 50) || '-',
 parent: parentInfo,
 visible,
 position: `${Math.round(rect.top)},${Math.round(rect.left)}`
 });
 });
 }
 });

 // Print summary
 console.log(' SUMMARY\n' + '='.repeat(60));
 console.log(`Total light mode elements found: ${summary.total}\n`);
 console.table(summary.byPattern);

 // Print top issues
 console.log('\n TOP ISSUES (visible elements)\n' + '='.repeat(60));
 const visibleIssues = issues.filter(i => i.visible).slice(0, 20);
 console.table(visibleIssues);

 // Generate report
 console.log('\n DETAILED REPORT\n' + '='.repeat(60));
 const report = {
 timestamp: new Date().toISOString(),
 url: window.location.href,
 summary,
 issues: visibleIssues
 };

 console.log('Copy this JSON and send to AI:');
 console.log(JSON.stringify(report, null, 2));

 // Also log as formatted text
 console.log('\n TEXT REPORT (easier to copy)\n' + '='.repeat(60));
 visibleIssues.forEach((issue, idx) => {
 console.log(`${idx + 1}. ${issue.pattern} on <${issue.tag}>`);
 console.log(` Classes: ${issue.classes}`);
 console.log(` Text: "${issue.text}"`);
 console.log(` Parent: ${issue.parent}`);
 console.log('');
 });

 return report;
}

// Auto-run
console.log(' Dark Theme Audit Tool Loaded!');
console.log('Run: runAudit()');

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
 module.exports = { runAudit };
}
