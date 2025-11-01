/**
 * RIK JavaScript Client - Example Usage
 * ======================================
 *
 * Run with: node example.js
 */

const RIKClient = require('./rik-client');

async function main() {
    console.log('🚀 RIK JavaScript Client - Example Usage\n');

    // Create client
    const client = new RIKClient('http://localhost:8000', {
        // apiKey: 'your-api-key-here',  // Optional
        timeout: 30000,  // 30 seconds
        maxRetries: 3
    });

    try {
        // ====================================================================
        // Example 1: Health Check
        // ====================================================================
        console.log('=' .repeat(60));
        console.log('Example 1: Health Check');
        console.log('=' .repeat(60));

        const isAlive = await client.isAlive();
        console.log(`API is alive: ${isAlive ? '✓' : '✗'}`);

        if (isAlive) {
            const health = await client.getHealth();
            console.log(`Health status: ${health.status}`);
            console.log('Subsystems:');
            for (const [system, status] of Object.entries(health.subsystems || {})) {
                console.log(`  ${status ? '✓' : '✗'} ${system}`);
            }

            const version = await client.getVersion();
            console.log(`\nVersion: ${version.version}`);
            console.log(`Environment: ${version.environment}`);
        }

        // ====================================================================
        // Example 2: Process Invoice
        // ====================================================================
        console.log('\n' + '='.repeat(60));
        console.log('Example 2: Process Invoice with Exceptions');
        console.log('='.repeat(60));

        const invoiceData = {
            invoice_number: 'INV-JS-001',
            vendor_name: 'Tech Solutions Inc',
            amount: 5500.00,
            date: '2024-11-01',
            po_number: '',  // Missing PO number - exception!
            extraction_confidence: 0.20  // Low confidence - another exception!
        };

        console.log('\n📄 Processing Invoice:');
        console.log(`   Invoice #: ${invoiceData.invoice_number}`);
        console.log(`   Vendor: ${invoiceData.vendor_name}`);
        console.log(`   Amount: $${invoiceData.amount.toFixed(2)}`);
        console.log(`   PO Number: ${invoiceData.po_number || '(MISSING)'}`);
        console.log(`   Confidence: ${(invoiceData.extraction_confidence * 100).toFixed(0)}%`);

        const invoiceResult = await client.processInvoice(
            JSON.stringify(invoiceData),
            invoiceData.invoice_number
        );

        console.log('\n🧠 RIK Analysis:');
        console.log(`   Final Action: ${invoiceResult.final_action.toUpperCase()}`);
        console.log(`   Confidence: ${(invoiceResult.confidence_score * 100).toFixed(0)}%`);
        console.log(`   Processing Time: ${invoiceResult.processing_time_seconds.toFixed(3)}s`);
        console.log(`   Exceptions Found: ${invoiceResult.exceptions_found}`);
        console.log(`   Exceptions Resolved: ${invoiceResult.exceptions_resolved}`);

        console.log('\n💡 Reasoning:');
        console.log(`   ${invoiceResult.reasoning}`);

        if (invoiceResult.traditional_rpa_would_fail) {
            console.log('\n📊 RPA Comparison:');
            console.log('   ✗ Traditional RPA: WOULD FAIL');
            console.log('   ✓ RIK: SUCCESS');
        }

        // ====================================================================
        // Example 3: Recover Web Scraper Selector
        // ====================================================================
        console.log('\n' + '='.repeat(60));
        console.log('Example 3: Recover Broken Selector');
        console.log('='.repeat(60));

        const html = `
            <div class="product-card">
                <h2 class="product-title">Premium Widget</h2>
                <div class="pricing-container">
                    <span class="price-tag price-current">$99.99</span>
                </div>
            </div>
        `;

        const failedSelector = '.old-price';  // This selector broke after redesign

        console.log(`\n🔍 Attempting to recover selector:`);
        console.log(`   Failed Selector: ${failedSelector}`);
        console.log(`   Target: Product price`);

        const selectorResult = await client.recoverSelector(
            failedSelector,
            html,
            'https://example.com/products/widget',
            { target_element: 'product price', example_value: '$99.99' }
        );

        console.log('\n✓ Selector Recovered!');
        console.log(`   New Selector: ${selectorResult.recovered_selector}`);
        console.log(`   Type: ${selectorResult.selector_type}`);
        console.log(`   Confidence: ${(selectorResult.confidence_score * 100).toFixed(0)}%`);

        console.log('\n💡 Reasoning:');
        console.log(`   ${selectorResult.reasoning}`);

        // Test the new selector
        const testResult = await client.testSelector(
            selectorResult.recovered_selector,
            html,
            selectorResult.selector_type
        );

        console.log('\n🧪 Testing new selector:');
        console.log(`   ${testResult.success ? '✓' : '✗'} Selector works!`);
        if (testResult.element_count) {
            console.log(`   Matched ${testResult.element_count} element(s)`);
        }

        // ====================================================================
        // Example 4: Get Metrics and Stats
        // ====================================================================
        console.log('\n' + '='.repeat(60));
        console.log('Example 4: Performance Metrics & ROI');
        console.log('='.repeat(60));

        const metrics = await client.getMetrics();
        console.log('\n📊 Performance Metrics:');
        console.log(`   Efficiency: ${(metrics.efficiency * 100).toFixed(1)}%`);
        console.log(`   Total Episodes: ${metrics.total_episodes}`);
        console.log(`   Successful: ${metrics.successful_episodes}`);
        console.log(`   Failed: ${metrics.failed_episodes}`);

        const stats = await client.getInvoiceStats();
        console.log('\n💰 Invoice Processing ROI:');
        console.log(`   Total Processed: ${stats.total_invoices_processed.toLocaleString()}`);
        console.log(`   RIK Automation Rate: ${(stats.automation_rate * 100).toFixed(1)}%`);
        console.log(`   Traditional RPA Rate: ${(stats.traditional_rpa_automation_rate * 100).toFixed(1)}%`);
        console.log(`   Improvement: ${stats.automation_improvement}`);
        console.log(`   Annual Savings: $${stats.annual_savings_usd.toLocaleString()}`);

        // ====================================================================
        // Example 5: Batch Processing
        // ====================================================================
        console.log('\n' + '='.repeat(60));
        console.log('Example 5: Batch Invoice Processing');
        console.log('='.repeat(60));

        const invoices = [
            { invoice_number: 'INV-001', vendor_name: 'Acme Corp', amount: 1000, po_number: 'PO-123' },
            { invoice_number: 'INV-002', vendor_name: 'TechCo', amount: 5000, po_number: '' },  // Missing PO
            { invoice_number: 'INV-003', vendor_name: 'SupplyCo', amount: 15000, po_number: 'PO-456' },
        ];

        console.log(`\n📋 Processing ${invoices.length} invoices...`);

        const results = await Promise.all(
            invoices.map(invoice =>
                client.processInvoice(JSON.stringify(invoice), invoice.invoice_number)
            )
        );

        const automated = results.filter(r => r.final_action !== 'escalate').length;
        const escalated = results.length - automated;

        console.log('\n📊 Batch Results:');
        console.log(`   Total: ${results.length}`);
        console.log(`   Automated: ${automated} (${(automated / results.length * 100).toFixed(0)}%)`);
        console.log(`   Escalated: ${escalated} (${(escalated / results.length * 100).toFixed(0)}%)`);

        console.log('\n📋 Individual Results:');
        results.forEach((result, i) => {
            const icon = result.final_action !== 'escalate' ? '✓' : '⚠️';
            console.log(`   ${icon} ${invoices[i].invoice_number}: ${result.final_action.toUpperCase()} ` +
                       `(confidence: ${(result.confidence_score * 100).toFixed(0)}%)`);
        });

        console.log('\n' + '='.repeat(60));
        console.log('✓ All examples completed!');
        console.log('='.repeat(60));

    } catch (error) {
        console.error('\n❌ Error:', error.message);
        if (error.name === 'RIKConnectionError') {
            console.error('   Make sure the RIK API is running:');
            console.error('   $ python3 rik_api.py');
        }
        if (error.details) {
            console.error('   Details:', error.details);
        }
        process.exit(1);
    }
}

// Run examples
main();
