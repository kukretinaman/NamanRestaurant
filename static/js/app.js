document.addEventListener( DOMContentLoaded,()=>{document.querySelectorAll([data-autoclose]).forEach(a=>{setTimeout(()=>{a.remove()},+a.dataset.autoclose||5000)})});
