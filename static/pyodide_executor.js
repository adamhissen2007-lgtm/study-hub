let pyodide;
let isPyodideReady = false;

async function initializePyodide() {
    if (isPyodideReady) return true;
    try {
        pyodide = await loadPyodide({ indexURL: "https://cdn.jsdelivr.net/pyodide/v0.25.0/full/" });
        isPyodideReady = true;
        return true;
    } catch (e) {
        console.error(e);
        return false;
    }
}

async function executePythonCode(code) {
    if (!isPyodideReady) await initializePyodide();
    try {
        pyodide.globals.set('_output', []);
        await pyodide.runPythonAsync(`
import sys
from io import StringIO
sys.stdout = StringIO()
        `);
        await pyodide.runPythonAsync(code);
        const stdout = await pyodide.runPythonAsync('sys.stdout.getvalue()');
        return { success: true, result: stdout || 'تم التنفيذ' };
    } catch (e) {
        return { success: false, error: e.message };
    }
}