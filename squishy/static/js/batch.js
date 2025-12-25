document.addEventListener('DOMContentLoaded', () => {
    // Listen for checkbox changes
    const checkboxes = document.querySelectorAll('.episode-checkbox');
    checkboxes.forEach(cb => {
        cb.addEventListener('change', updateBatchUI);
    });

    // Select All / None
    const selectAllBtn = document.getElementById('selectAllBtn');
    if (selectAllBtn) {
        selectAllBtn.addEventListener('click', () => {
            checkboxes.forEach(cb => cb.checked = true);
            updateBatchUI();
        });
    }

    const selectNoneBtn = document.getElementById('selectNoneBtn');
    if (selectNoneBtn) {
        selectNoneBtn.addEventListener('click', () => {
            checkboxes.forEach(cb => cb.checked = false);
            updateBatchUI();
        });
    }

    // Floating Action Bar
    const batchActionBar = document.getElementById('batchActionBar');
    const batchCountSpan = document.getElementById('batchSelectedCount');
    const batchSquishBtn = document.getElementById('batchSquishBtn');

    function updateBatchUI() {
        const selected = document.querySelectorAll('.episode-checkbox:checked');
        const count = selected.length;

        if (count > 0) {
            batchActionBar.classList.add('visible');
            batchCountSpan.textContent = count;
        } else {
            batchActionBar.classList.remove('visible');
        }
    }

    // Batch Squish Button Click
    if (batchSquishBtn) {
        batchSquishBtn.addEventListener('click', () => {
            const modal = document.getElementById('squishModal');
            if (modal) {
                // Set modal mode to batch
                modal.dataset.mode = 'batch';
                document.getElementById('squishModalTitle').textContent = `Squish ${document.getElementById('batchSelectedCount').textContent} Items`;
                modal.classList.remove('hidden');
            }
        });
    }

    // Hijack squish form submit for batch mode
    const squishForm = document.getElementById('squishForm');
    if (squishForm) {
        squishForm.addEventListener('submit', async (e) => {
            const modal = document.getElementById('squishModal');
            if (modal.dataset.mode === 'batch') {
                e.preventDefault();

                const preset = document.getElementById('squishProfile').value;
                const selected = Array.from(document.querySelectorAll('.episode-checkbox:checked')).map(cb => cb.value);

                try {
                    const response = await fetch('/batch/transcode', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            media_ids: selected,
                            preset_name: preset
                        })
                    });

                    const result = await response.json();
                    if (result.success) {
                        window.location.reload(); // Reload to show new jobs (or redirect to jobs)
                    } else {
                        alert('Error: ' + result.message);
                    }
                } catch (err) {
                    alert('Error submitting batch job');
                    console.error(err);
                }
            }
        });
    }
});

// Helper for "Squish Season" buttons
function selectSeason(seasonId) {
    const checkboxes = document.querySelectorAll(`.season-${seasonId} .episode-checkbox`);
    checkboxes.forEach(cb => cb.checked = true);
    // Scroll to action bar or just show it
    const batchActionBar = document.getElementById('batchActionBar');
    if (batchActionBar) {
        // Trigger update
        const event = new Event('change');
        if (checkboxes.length > 0) checkboxes[0].dispatchEvent(event);
    }
}
