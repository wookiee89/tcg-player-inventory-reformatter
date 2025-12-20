// Run this in the browser console on https://www.tcgplayer.com/massentry
// After the page loads and you select "Magic: The Gathering" as the product line

// Method 1: Try to find the element at the specified XPath
const xpath = "/html/body/div[2]/div/div/section[2]/section/div[1]/div[2]/div[1]/div[1]/div/div[3]/div/div/div/section[2]/section/div[2]";
const result = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
const element = result.singleNodeValue;

if (element) {
    console.log("Found element at XPath!");
    console.log("Element:", element);
    console.log("Text content:", element.textContent);
    console.log("HTML:", element.innerHTML);
    
    // Try to extract set codes
    const setCodes = [];
    
    // Look for data attributes
    const dataAttrs = Array.from(element.attributes).filter(attr => 
        attr.name.toLowerCase().includes('set') || attr.name.toLowerCase().includes('code')
    );
    console.log("Data attributes:", dataAttrs);
    
    // Look for child elements that might contain set codes
    const children = element.querySelectorAll('*');
    children.forEach(child => {
        // Check text content
        const text = child.textContent?.trim();
        if (text && text.length <= 10 && /^[A-Z0-9]+$/.test(text)) {
            setCodes.push(text);
        }
        
        // Check data attributes
        Array.from(child.attributes).forEach(attr => {
            if (attr.name.toLowerCase().includes('set') || attr.name.toLowerCase().includes('code')) {
                console.log(`Found attribute: ${attr.name} = ${attr.value}`);
            }
        });
    });
    
    console.log("Potential set codes found:", [...new Set(setCodes)]);
} else {
    console.log("Element not found at XPath. Trying alternative methods...");
    
    // Method 2: Search for elements with set-related attributes
    const setElements = document.querySelectorAll('[data-set], [data-set-code], [data-setcode], [data-code]');
    console.log(`Found ${setElements.length} elements with set-related attributes`);
    setElements.forEach((el, i) => {
        if (i < 10) {
            console.log(`Element ${i}:`, el, el.getAttribute('data-set') || el.getAttribute('data-set-code') || el.getAttribute('data-code'));
        }
    });
    
    // Method 3: Look for select/dropdown elements
    const selects = document.querySelectorAll('select');
    console.log(`\nFound ${selects.length} select elements`);
    selects.forEach((select, i) => {
        if (i < 5) {
            console.log(`Select ${i}:`, select);
            const options = Array.from(select.options);
            console.log(`  Options:`, options.slice(0, 10).map(opt => ({
                text: opt.text,
                value: opt.value
            })));
        }
    });
    
    // Method 4: Search in React component state (if accessible)
    if (window.__REACT_DEVTOOLS_GLOBAL_HOOK__) {
        console.log("\nReact DevTools available - you can inspect component state");
    }
    
    // Method 5: Look for API calls in network tab
    console.log("\nTip: Check Network tab for API calls containing 'set' or 'productline'");
}

