document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('cv-upload-form');
    const resultsContainer = document.getElementById('results-container');

    form.addEventListener('submit', function(event) {
        event.preventDefault();
        
        const formData = new FormData(form);
        
        fetch('/process_cvs', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            displayResults(data);
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });

    function displayResults(data) {
        resultsContainer.innerHTML = '';
        if (data.length === 0) {
            resultsContainer.innerHTML = '<p>No candidates shortlisted.</p>';
            return;
        }

        const ul = document.createElement('ul');
        data.forEach(candidate => {
            const li = document.createElement('li');
            li.textContent = `${candidate.name} - Score: ${candidate.score}`;
            ul.appendChild(li);
        });
        resultsContainer.appendChild(ul);
    }
});