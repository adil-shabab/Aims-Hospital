document.addEventListener('DOMContentLoaded', function () {
    var wrapper = document.querySelector(".main-wrapper");
    var pageWrapper = document.querySelector(".page-wrapper");
    var slimScrolls = document.querySelectorAll(".slimscroll");
    var sidebarOverlay = document.querySelector(".sidebar-overlay");

    function Sidemenu() {
        this.menuItems = document.querySelectorAll("#sidebar-menu a");
    }

    function init() {
        var sidemenu = new Sidemenu();
        sidemenu.menuItems.forEach(function (item) {
            item.addEventListener("click", function (e) {
                if (item.parentElement.classList.contains("submenu")) {
                    e.preventDefault();
                }
                if (!item.classList.contains("subdrop")) {
                    item.closest("ul").querySelectorAll("ul").forEach(function (ul) {
                        ul.style.display = "none";
                    });
                    item.closest("ul").querySelectorAll("a").forEach(function (a) {
                        a.classList.remove("subdrop");
                    });
                    item.nextElementSibling.style.display = "block";
                    item.classList.add("subdrop");
                } else if (item.classList.contains("subdrop")) {
                    item.classList.remove("subdrop");
                    item.nextElementSibling.style.display = "none";
                }
            });
        });
    }
    init();

    function sidebarOverlayToggle(target) {
        if (target) {
            target.classList.toggle("opened");
            sidebarOverlay.classList.toggle("opened");
            document.documentElement.classList.toggle("menu-opened");
            sidebarOverlay.setAttribute("data-reff", "#" + target.id);
        }
    }

    document.querySelector("#mobile_btn").addEventListener("click", function (e) {
        var target = document.querySelector(this.getAttribute("href"));
        sidebarOverlayToggle(target);
        wrapper.classList.toggle("slide-nav");
        document.querySelector("#chat_sidebar").classList.remove("opened");
        e.preventDefault();
    });


    sidebarOverlay.addEventListener("click", function () {
        var target = document.querySelector(this.getAttribute("data-reff"));
        if (target) {
            target.classList.remove("opened");
            document.documentElement.classList.remove("menu-opened");
            this.classList.remove("opened");
            wrapper.classList.remove("slide-nav");
        }
    });

    document.querySelectorAll(".toggle-password").forEach(function (el) {
        el.addEventListener("click", function () {
            el.classList.toggle("feather-eye-off");
            el.classList.toggle("feather-eye");
            var input = document.querySelector(".pass-input");
            input.setAttribute("type", input.getAttribute("type") === "password" ? "text" : "password");
        });
    });

    document.querySelectorAll(".confirm-password").forEach(function (el) {
        el.addEventListener("click", function () {
            el.classList.toggle("feather-eye-off");
            el.classList.toggle("feather-eye");
            var input = document.querySelector(".pass-input-confirm");
            input.setAttribute("type", input.getAttribute("type") === "password" ? "text" : "password");
        });
    });

    function animateElements() {
        document.querySelectorAll(".circle-bar2").forEach(function (el) {
            var elementPos = el.getBoundingClientRect().top + window.scrollY;
            var topOfWindow = window.scrollY;
            var percent = el.querySelector(".circle-graph2").getAttribute("data-percent");
            var animate = el.getAttribute("data-animate");
            if (elementPos < topOfWindow + window.innerHeight - 30 && !animate) {
                el.setAttribute("data-animate", true);
                new CircleProgress(el.querySelector(".circle-graph2"), { value: percent / 100, size: 400, thickness: 30, fill: { color: "#00a6c8" } });
            }
        });
    }

    if (document.querySelectorAll(".circle-bar").length > 0) {
        animateElements();
    }
    window.addEventListener("scroll", animateElements);

    if (document.querySelectorAll(".select").length > 0) {
        document.querySelectorAll(".select").forEach(function (el) {
            new Select2(el, { minimumResultsForSearch: -1, width: "100%" });
        });
    }

    if (document.querySelectorAll(".floating").length > 0) {
        document.querySelectorAll(".floating").forEach(function (el) {
            el.addEventListener("focus", function () {
                el.closest(".form-focus").classList.add("focused");
            });
            el.addEventListener("blur", function () {
                if (el.value.length === 0) {
                    el.closest(".form-focus").classList.remove("focused");
                }
            });
            el.dispatchEvent(new Event('blur'));
        });
    }

    if (document.querySelector("#msg_list")) {
        new SlimScroll(document.querySelector("#msg_list"), { height: "100%", color: "#878787", disableFadeOut: true, borderRadius: 0, size: "4px", alwaysVisible: false, touchScrollStep: 100 });
        var msgHeight = window.innerHeight - 124;
        document.querySelector("#msg_list").style.height = msgHeight + "px";
        document.querySelector(".msg-sidebar .slimScrollDiv").style.height = msgHeight + "px";
        window.addEventListener("resize", function () {
            var msgrHeight = window.innerHeight - 124;
            document.querySelector("#msg_list").style.height = msgrHeight + "px";
            document.querySelector(".msg-sidebar .slimScrollDiv").style.height = msgrHeight + "px";
        });
    }

    var pHeight = window.innerHeight;
    pageWrapper.style.minHeight = pHeight + "px";
    window.addEventListener("resize", function () {
        var prHeight = window.innerHeight;
        pageWrapper.style.minHeight = prHeight + "px";
    });

    if (document.querySelectorAll(".datetimepicker").length > 0) {
        document.querySelectorAll(".datetimepicker").forEach(function (el) {
            new DateTimePicker(el, { format: "DD/MM/YYYY", icons: { up: "fas fa-angle-up", down: "fas fa-angle-down", next: "fas fa-angle-right", previous: "fas fa-angle-left" } });
        });
    }

    if (document.querySelectorAll(".summernote").length > 0) {
        document.querySelectorAll(".summernote").forEach(function (el) {
            new Summernote(el, {
                placeholder: "Description",
                focus: true,
                minHeight: 100,
                disableResizeEditor: false,
                toolbar: [
                    ["fullscreen"],
                    ["fontname", ["fontname"]],
                    ["undo"],
                    ["redo"],
                    ["datetimepicker"],
                    ["fontsize", ["fontsize"]],
                    ["font", ["bold", "italic", "underline", "clear"]],
                    ["color", ["color"]],
                    ["para", ["ul", "ol", "paragraph"]],
                    ["insert", ["link", "picture"]],
                ],
            });
        });
    }

    if (document.querySelector("#summernote")) {
        new Summernote(document.querySelector("#summernote"), { height: 300, minHeight: null, maxHeight: null, focus: true });
    }

    if (document.querySelector("#editor")) {
        ClassicEditor.create(document.querySelector("#editor"), {
            toolbar: {
                items: [
                    "heading",
                    "|",
                    "fontfamily",
                    "fontsize",
                    "|",
                    "alignment",
                    "|",
                    "fontColor",
                    "fontBackgroundColor",
                    "|",
                    "bold",
                    "italic",
                    "strikethrough",
                    "underline",
                    "subscript",
                    "superscript",
                    "|",
                    "link",
                    "|",
                    "outdent",
                    "indent",
                    "|",
                    "bulletedList",
                    "numberedList",
                    "todoList",
                    "|",
                    "code",
                    "codeBlock",
                    "|",
                    "insertTable",
                    "|",
                    "uploadImage",
                    "blockQuote",
                    "|",
                    "undo",
                    "redo",
                ],
                shouldNotGroupWhenFull: true,
            },
        }).then((editor) => {
            window.editor = editor;
        }).catch((err) => {
            console.error(err.stack);
        });
    }

    if (document.querySelectorAll(".counter").length > 0) {
        document.querySelectorAll(".counter").forEach(function (el) {
            new CounterUp(el, { delay: 20, time: 2000 });
        });
    }

    if (document.querySelector("#timer-countdown")) {
        new Countdown(document.querySelector("#timer-countdown"), { from: 180, to: 0, movingUnit: 1000, timerEnd: undefined, outputPattern: "$day Day $hour : $minute : $second", autostart: true });
    }

    if (document.querySelector("#timer-countup")) {
        new Countdown(document.querySelector("#timer-countup"), { from: 0, to: 180 });
    }

    if (document.querySelector("#timer-countinbetween")) {
        new Countdown(document.querySelector("#timer-countinbetween"), { from: 30, to: 20 });
    }

    if (document.querySelector("#timer-countercallback")) {
        new Countdown(document.querySelector("#timer-countercallback"), {
            from: 10,
            to: 0,
            timerEnd: function () {
                this.style.textDecoration = "line-through";
                this.style.opacity = 0.5;
            },
        });
    }

    if (document.querySelector("#timer-outputpattern")) {
        new Countdown(document.querySelector("#timer-outputpattern"), { outputPattern: "$day Days $hour Hour $minute Min $second Sec..", from: 60 * 60 * 24 * 3 });
    }

    if (document.querySelectorAll(".clipboard").length > 0) {
        document.querySelectorAll(".btn").forEach(function (el) {
            new Clipboard(el);
        });
    }

    if (document.querySelectorAll('[data-bs-toggle="popover"]').length > 0) {
        var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    }

    document.querySelectorAll(".next").forEach(function (el) {
        el.addEventListener("click", function () {
            el.closest(".tab-pane").nextElementSibling.style.display = "block";
            el.closest(".tab-pane").style.display = "none";
        });
    });

    document.querySelectorAll(".previous").forEach(function (el) {
        el.addEventListener("click", function () {
            el.closest(".tab-pane").previousElementSibling.style.display = "block";
            el.closest(".tab-pane").style.display = "none";
        });
    });

    if (document.querySelectorAll('[data-bs-toggle="tooltip"]').length > 0) {
        document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function (el) {
            new bootstrap.Tooltip(el);
        });
    }

    if (document.querySelectorAll(".custom-file-container").length > 0) {
        var firstUpload = new FileUploadWithPreview("myFirstImage");
        var secondUpload = new FileUploadWithPreview("mySecondImage");
    }

    if (document.querySelector("#editor")) {
        ClassicEditor.create(document.querySelector("#editor"), {
            toolbar: {
                items: [
                    "heading",
                    "|",
                    "fontfamily",
                    "fontsize",
                    "|",
                    "alignment",
                    "|",
                    "fontColor",
                    "fontBackgroundColor",
                    "|",
                    "bold",
                    "italic",
                    "strikethrough",
                    "underline",
                    "subscript",
                    "superscript",
                    "|",
                    "link",
                    "|",
                    "outdent",
                    "indent",
                    "|",
                    "bulletedList",
                    "numberedList",
                    "todoList",
                    "|",
                    "code",
                    "codeBlock",
                    "|",
                    "insertTable",
                    "|",
                    "uploadImage",
                    "blockQuote",
                    "|",
                    "undo",
                    "redo",
                ],
                shouldNotGroupWhenFull: true,
            },
        }).then((editor) => {
            window.editor = editor;
        }).catch((err) => {
            console.error(err.stack);
        });
    }



    if (document.querySelector("#datetimepicker3")) {
        new DateTimePicker(document.querySelector("#datetimepicker3"), { format: "LT", icons: { up: "fas fa-angle-up", down: "fas fa-angle-down", next: "fas fa-angle-right", previous: "fas fa-angle-left" } });
    }

    if (document.querySelector("#datetimepicker4")) {
        new DateTimePicker(document.querySelector("#datetimepicker4"), { format: "LT", icons: { up: "fas fa-angle-up", down: "fas fa-angle-down", next: "fas fa-angle-right", previous: "fas fa-angle-left" } });
    }

    if (document.querySelectorAll(".center").length > 0) {
        document.querySelectorAll(".center").forEach(function (el) {
            new Slick(el, {
                centerMode: true,
                arrows: false,
                centerPadding: "30px",
                slidesToShow: 3,
                responsive: [
                    { breakpoint: 768, settings: { arrows: false, centerMode: true, centerPadding: "40px", slidesToShow: 3 } },
                    { breakpoint: 480, settings: { arrows: false, centerMode: true, centerPadding: "40px", slidesToShow: 3 } },
                ],
            });
        });
    }

    if (document.querySelectorAll('[data-toggle="tooltip"]').length > 0) {
        document.querySelectorAll('[data-toggle="tooltip"]').forEach(function (el) {
            new bootstrap.Tooltip(el);
        });
    }


    if (document.querySelector("#lightgallery")) {
        new LightGallery(document.querySelector("#lightgallery"), { thumbnail: true, selector: "a" });
    }

    if (document.querySelector("#incoming_call")) {
        new bootstrap.Modal(document.querySelector("#incoming_call")).show();
    }


    if (document.querySelectorAll(".summernote").length > 0) {
        document.querySelectorAll(".summernote").forEach(function (el) {
            new Summernote(el, { height: 200, minHeight: null, maxHeight: null, focus: false });
        });
    }



    if (document.querySelectorAll(".checkmail").length > 0) {
        document.querySelectorAll(".checkmail").forEach(function (el) {
            el.addEventListener("click", function () {
                if (el.closest("tr").classList.contains("checked")) {
                    el.closest("tr").classList.remove("checked");
                } else {
                    el.closest("tr").classList.add("checked");
                }
            });
        });
    }

    document.querySelectorAll(".mail-important").forEach(function (el) {
        el.addEventListener("click", function () {
            el.querySelector("i.fa").classList.toggle("fa-star");
            el.querySelector("i.fa").classList.toggle("fa-star-o");
        });
    });

    if (document.querySelector("#drop-zone")) {
        var dropZone = document.querySelector("#drop-zone");
        var uploadForm = document.querySelector("#js-upload-form");
        var startUpload = function (files) {
            console.log(files);
        };
        uploadForm.addEventListener("submit", function (e) {
            var uploadFiles = document.querySelector("#js-upload-files").files;
            e.preventDefault();
            startUpload(uploadFiles);
        });
        dropZone.ondrop = function (e) {
            e.preventDefault();
            this.className = "upload-drop-zone";
            startUpload(e.dataTransfer.files);
        };
        dropZone.ondragover = function () {
            this.className = "upload-drop-zone drop";
            return false;
        };
        dropZone.ondragleave = function () {
            this.className = "upload-drop-zone";
            return false;
        };
    }

    if (window.innerWidth >= 992) {
        document.querySelector("#toggle_btn").addEventListener("click", function () {
            if (document.body.classList.contains("mini-sidebar")) {
                document.body.classList.remove("mini-sidebar");
                document.querySelectorAll(".subdrop + ul").forEach(function (el) {
                    el.style.display = "block";
                });
            } else {
                document.body.classList.add("mini-sidebar");
                document.querySelectorAll(".subdrop + ul").forEach(function (el) {
                    el.style.display = "none";
                });
            }
        });

        document.addEventListener("mouseover", function (e) {
            e.stopPropagation();
            if (document.body.classList.contains("mini-sidebar") && document.querySelector("#toggle_btn").offsetParent !== null) {
                var targ = e.target.closest(".sidebar");
                if (targ) {
                    document.body.classList.add("expand-menu");
                    document.querySelectorAll(".subdrop + ul").forEach(function (el) {
                        el.style.display = "block";
                    });
                } else {
                    document.body.classList.remove("expand-menu");
                    document.querySelectorAll(".subdrop + ul").forEach(function (el) {
                        el.style.display = "none";
                    });
                }
            }
        });
    }

    if (document.querySelectorAll("[data-feather]").length > 0) {
        feather.replace();
    }

    document.querySelectorAll(".app-listing .selectBox").forEach(function (el) {
        el.addEventListener("click", function () {
            el.parentElement.querySelector("#checkBoxes").classList.toggle("fade");
            el.parentElement.parentElement.querySelectorAll("#checkBoxes").forEach(function (el) {
                el.classList.remove("fade");
            });
        });
    });

    document.querySelectorAll(".invoices-main-form .selectBox").forEach(function (el) {
        el.addEventListener("click", function () {
            el.parentElement.querySelector("#checkBoxes-one").classList.toggle("fade");
            el.parentElement.parentElement.querySelectorAll("#checkBoxes-one").forEach(function (el) {
                el.classList.remove("fade");
            });
        });
    });




    if (document.querySelector("#editor")) {
        ClassicEditor.create(document.querySelector("#editor"), { toolbar: ["bold", "italic", "link"] })
            .then((editor) => {
                window.editor = editor;
            })
            .catch((err) => {
                console.error(err.stack);
            });
    }




});
