// assets/export_pdf.js
// Export PDF avec mise en page améliorée (évite la coupure de texte)

(function () {
    if (window.dash_export_pdf_initialized) return;
    window.dash_export_pdf_initialized = true;

    function exportDashboardToPDF() {
        const root = document.getElementById("page-wrapper");
        if (!root) {
            alert("Impossible de trouver la zone #page-wrapper à exporter.");
            return;
        }
        if (typeof html2canvas === "undefined") {
            alert("html2canvas n'est pas chargé (vérifie external_scripts dans app.py).");
            return;
        }
        if (!window.jspdf || !window.jspdf.jsPDF) {
            alert("jsPDF n'est pas chargé (vérifie external_scripts dans app.py).");
            return;
        }

        const { jsPDF } = window.jspdf;
        const originalOverflow = document.body.style.overflow;
        document.body.style.overflow = "visible";
        document.body.style.cursor = "progress";

        // Petite pause pour que le DOM se stabilise
        setTimeout(function () {
            html2canvas(root, {
                scale: 1.5,           // réduit la résolution pour éviter les coupures
                useCORS: true,
                allowTaint: true,
                scrollX: 0,
                scrollY: -window.scrollY,
                windowWidth: document.documentElement.scrollWidth,
                windowHeight: document.documentElement.scrollHeight,
                logging: false,
            })
            .then(function (canvas) {
                const imgData = canvas.toDataURL("image/jpeg", 0.90);

                // Format A4 paysage
                const pdf = new jsPDF({
                    orientation: "landscape",
                    unit: "mm",
                    format: "a4",
                });

                const pageW = pdf.internal.pageSize.getWidth();
                const pageH = pdf.internal.pageSize.getHeight();

                // Calcul du ratio pour faire rentrer la largeur en une page
                const ratio = pageW / canvas.width;
                const imgW  = pageW;
                const imgH  = canvas.height * ratio;

                // Découpage en pages avec chevauchement minimal
                const margin     = 8;       // marge haute/basse (mm)
                const usableH    = pageH - 2 * margin;
                let posY         = 0;       // position dans l'image totale (mm)
                let firstPage    = true;

                while (posY < imgH) {
                    if (!firstPage) pdf.addPage();
                    firstPage = false;

                    pdf.addImage(
                        imgData,
                        "JPEG",
                        0,                          // x
                        margin - posY,              // y (négatif = décale l'image vers le haut)
                        imgW,
                        imgH,
                        undefined,
                        "FAST"
                    );

                    posY += usableH;
                }

                pdf.save("copublications_inria.pdf");
            })
            .catch(function (err) {
                console.error("Erreur export PDF :", err);
                alert("Erreur lors de la génération du PDF. Voir la console.");
            })
            .finally(function () {
                document.body.style.overflow = originalOverflow;
                document.body.style.cursor   = "default";
            });
        }, 200);
    }

    // Délégation d'événement : fonctionne même si le bouton est créé dynamiquement
    document.addEventListener("click", function (e) {
        const btn = e.target.closest("#export-pdf");
        if (!btn) return;
        e.preventDefault();
        exportDashboardToPDF();
    });
})();