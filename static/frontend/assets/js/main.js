/*=== Javascript function indexing hear===========

1.counterUp ----------(Its use for counting number)
2.stickyHeader -------(header class sticky)
3.wowActive ----------( Waw js plugins activation)
4.swiperJs -----------(All swiper in this website hear)
5.salActive ----------(Sal animation for card and all text)
6.textChanger --------(Text flip for banner section)
7.timeLine -----------(History Time line)
8.datePicker ---------(On click date calender)
9.timePicker ---------(On click time picker)
10.timeLineStory -----(History page time line)
11.vedioActivation----(Vedio activation)
12.searchOption ------(search open)
13.cartBarshow -------(Cart sode bar)
14.sideMenu ----------(Open side menu for desktop)
15.Back to top -------(back to top)
16.filterPrice -------(Price filtering)

==================================================*/

(function ($) {
  'use strict';

  var rtsJs = {
    m: function (e) {
      rtsJs.d();
      rtsJs.methods();
    },
    d: function (e) {
      this._window = $(window),
        this._document = $(document),
        this._body = $('body'),
        this._html = $('html')
    },
    methods: function (e) {
      rtsJs.metismenu();
      rtsJs.afterBefore();
      rtsJs.swiperActive();
      rtsJs.wowActive();
      rtsJs.stickyHeader();
      rtsJs.backToTopInit();
      rtsJs.sideMenu();
      rtsJs.vedioActivation();
      rtsJs.menuCurrentLink();
      rtsJs.preloader();
      rtsJs.datePicker();
    },


    metismenu: function () {
      $('#mobile-menu-active').metisMenu();
    },

    afterBefore: function () {
      $(document).ready(function () {

        if ($(".comparison-slider")[0]) {
          let compSlider = $(".comparison-slider");

          compSlider.each(function () {
            let compSliderWidth = $(this).width() + "px";
            $(this).find(".resize img").css({ width: compSliderWidth });
            drags($(this).find(".divider"), $(this).find(".resize"), $(this));
          });

          $(window).on("resize", function () {
            let compSliderWidth = compSlider.width() + "px";
            compSlider.find(".resize img").css({ width: compSliderWidth });
          });
        }
      });
      function drags(dragElement, resizeElement, container) {

        let touched = false;
        window.addEventListener('touchstart', function () {
          touched = true;
        });
        window.addEventListener('touchend', function () {
          touched = false;
        });

        dragElement.on("mousedown touchstart", function (e) {

          dragElement.addClass("draggable");
          resizeElement.addClass("resizable");
          //create vars
          let startX = e.pageX ? e.pageX : e.originalEvent.touches[0].pageX;
          let dragWidth = dragElement.outerWidth();
          let posX = dragElement.offset().left + dragWidth - startX;
          let containerOffset = container.offset().left;
          let containerWidth = container.outerWidth();
          let minLeft = containerOffset + 10;
          let maxLeft = containerOffset + containerWidth - dragWidth - 10;

          dragElement.parents().on("mousemove touchmove", function (e) {

            if (touched === false) {
              e.preventDefault();
            }

            let moveX = e.pageX ? e.pageX : e.originalEvent.touches[0].pageX;
            let leftValue = moveX + posX - dragWidth;

            if (leftValue < minLeft) {
              leftValue = minLeft;
            } else if (leftValue > maxLeft) {
              leftValue = maxLeft;
            }

            let widthValue = (leftValue + dragWidth / 2 - containerOffset) * 100 / containerWidth + "%";

            $(".draggable").css("left", widthValue).on("mouseup touchend touchcancel", function () {
              $(this).removeClass("draggable");
              resizeElement.removeClass("resizable");
            });

            $(".resizable").css("width", widthValue);

          }).on("mouseup touchend touchcancel", function () {
            dragElement.removeClass("draggable");
            resizeElement.removeClass("resizable");

          });

        }).on("mouseup touchend touchcancel", function (e) {
          dragElement.removeClass("draggable");
          resizeElement.removeClass("resizable");

        });

      }


    },

    swiperActive: function () {
      $(document).ready(function () {
        var swiper = new Swiper(".swiper-container-h1", {
          spaceBetween: 30,
          slidesPerView: 3,
          loop: true,
          speed: 1000,
          // autoplay: {
          //   delay: 3000,
          //   disableOnInteraction: false,
          // },
          navigation: {
            nextEl: ".swiper-button-next",
            prevEl: ".swiper-button-prev",
          },
          pagination: {
            el: ".swiper-pagination",
            clickable: true,
          },
          breakpoints: {
            1500: {
              slidesPerView: 3,
            },
            1199: {
              slidesPerView: 3,
            },
            991: {
              slidesPerView: 2,
            },
            767: {
              slidesPerView: 2,
            },
            575: {
              slidesPerView: 1,
            },
            0: {
              slidesPerView: 1,
            }
          },
        });
      });

      $(document).ready(function () {
        var swiper = new Swiper(".team-swiper-container-h1", {
          spaceBetween: 30,
          slidesPerView: 4,
          loop: true,
          speed: 1000,
          // autoplay: {
          //   delay: 3000,
          //   disableOnInteraction: false,
          // },
          navigation: {
            nextEl: ".swiper-button-next",
            prevEl: ".swiper-button-prev",
          },
          pagination: {
            el: ".swiper-pagination",
            clickable: true,
          },
          breakpoints: {
            1500: {
              slidesPerView: 4,
            },
            1199: {
              slidesPerView: 3,
            },
            991: {
              slidesPerView: 2,
            },
            767: {
              slidesPerView: 2,
            },
            575: {
              slidesPerView: 1,
            },
            0: {
              slidesPerView: 1,
            }
          },
        });
      });

      $(document).ready(function () {
        var swiper = new Swiper(".swiper-container-h1-team", {
          spaceBetween: 30,
          slidesPerView: 4,
          loop: true,
          speed: 1000,
          autoplay: {
            delay: 2000,
            disableOnInteraction: false,
          },
          pagination: {
            el: ".swiper-pagination",
            clickable: true,
          },
          breakpoints: {
            1500: {
              slidesPerView: 3,
            },
            1199: {
              slidesPerView: 3,
            },
            991: {
              slidesPerView: 3,
            },
            767: {
              slidesPerView: 2,
            },
            575: {
              slidesPerView: 1,
            },
            0: {
              slidesPerView: 1,
            }
          },
        });
      });
      $(document).ready(function () {
        var swiper = new Swiper(".swiper-container-h1-team-8", {
          spaceBetween: 150,
          slidesPerView: 4,
          loop: true,
          speed: 1000,
          autoplay: {
            delay: 2000,
            disableOnInteraction: false,
          },
          pagination: {
            el: ".swiper-pagination",
            clickable: true,
          },
          breakpoints: {
            1500: {
              slidesPerView: 3,
            },
            1199: {
              slidesPerView: 3,
            },
            991: {
              slidesPerView: 3,
            },
            767: {
              slidesPerView: 2,
            },
            575: {
              slidesPerView: 1,
            },
            0: {
              slidesPerView: 1,
            }
          },
        });
      });

      $(document).ready(function () {

        var swiper = new Swiper(".swiper-container-h3", {
          spaceBetween: 30,
          slidesPerView: 4,
          loop: true,
          speed: 1000,
          autoplay: {
            delay: 2000,
          },
          pagination: {
            el: ".swiper-pagination",
            clickable: true,
          },
          navigation: {
            nextEl: ".swiper-button-next",
            prevEl: ".swiper-button-prev",
          },
          breakpoints: {
            1500: {
              slidesPerView: 3,
            },
            1199: {
              slidesPerView: 3,
            },
            991: {
              slidesPerView: 2,
            },
            767: {
              slidesPerView: 2,
            },
            575: {
              slidesPerView: 1,
            },
            0: {
              slidesPerView: 1,
            }
          },
        });
      });

      $(document).ready(function () {
        var swiper = new Swiper(".swiper-container-h1.v3", {
          spaceBetween: 30,
          slidesPerView: 4,
          loop: true,
          speed: 1000,
          autoplay: {
            delay: 2000,
            disableOnInteraction: false,
          },
          pagination: {
            el: ".swiper-pagination",
            clickable: true,
          },
        });
        $('a[data-bs-toggle="tab"]').on('shown.bs.tab', function (e) {
          // Update Swiper when the tab with swiper is shown
          swiper.update();
        });
      });


      $(document).ready(function () {
        var swiper = new Swiper(".swiper-container-h2", {
          spaceBetween: 30,
          slidesPerView: 4,
          loop: true,
          speed: 1000,
          autoplay: {
            delay: 2000,
            disableOnInteraction: false,
          },
          pagination: {
            el: ".swiper-pagination",
            clickable: true,
          },
          breakpoints: {
            1500: {
              slidesPerView: 3,
            },
            1199: {
              slidesPerView: 3,
            },
            991: {
              slidesPerView: 2,
            },
            767: {
              slidesPerView: 2,
            },
            575: {
              slidesPerView: 1,
            },
            0: {
              slidesPerView: 1,
            }
          },
        });
      });

      $(document).ready(function () {
        var swiper = new Swiper(".home_page_banner_desktop", {
          spaceBetween: 0,
          slidesPerView: 1,
          loop: true,
          speed: 2000,
          effect: "fade",
          autoplay: {
            delay: 4000,
            disableOnInteraction: false,
          },
          navigation: {
            nextEl: ".swiper-button-next",
            prevEl: ".swiper-button-prev",
          },
        });
      });
      $(document).ready(function () {
        var swiper = new Swiper(".home_page_banner_mobile", {
          spaceBetween: 0,
          slidesPerView: 1,
          loop: true,
          speed: 2000,
          effect: "fade",
          autoplay: {
            delay: 4000,
            disableOnInteraction: false,
          },
          navigation: {
            nextEl: ".swiper-button-next",
            prevEl: ".swiper-button-prev",
          },
        });
      });
      $(document).ready(function () {
        var swiper = new Swiper(".mySwiper-banner-eight", {
          spaceBetween: 0,
          slidesPerView: 1,
          loop: true,
          speed: 1000,
          effect: "fade",
          autoplay: {
            delay: 3000,
            disableOnInteraction: false,
          },
          navigation: {
            nextEl: ".swiper-button-next",
            prevEl: ".swiper-button-prev",
          },
        });
      });

      $(document).ready(function () {
        var swiper = new Swiper(".mySwiper-brand", {
          spaceBetween: 65,
          slidesPerView: 5,
          loop: true,
          speed: 2000,
          autoplay: {
            delay: 4000,
            disableOnInteraction: false,
          },
          navigation: {
            nextEl: ".swiper-button-next",
            prevEl: ".swiper-button-prev",
          },
          breakpoints: {
            1500: {
              slidesPerView: 4,
            },
            1199: {
              slidesPerView: 4,
            },
            991: {
              slidesPerView: 4,
            },
            767: {
              slidesPerView: 3,
            },
            575: {
              slidesPerView: 3,
            },
            0: {
              slidesPerView: 2,
            }
          },
        });
      });

      $(document).ready(function () {
        var swiper = new Swiper(".mySwiper-service-dental", {
          spaceBetween: 30,
          slidesPerView: 4,
          loop: true,
          speed: 2000,
          autoplay: {
            delay: 4000,
            disableOnInteraction: false,
          },
          navigation: {
            nextEl: ".swiper-button-next",
            prevEl: ".swiper-button-prev",
          },
          breakpoints: {
            1500: {
              slidesPerView: 4,
            },
            1199: {
              slidesPerView: 3,
            },
            991: {
              slidesPerView: 2,
            },
            767: {
              slidesPerView: 2,
            },
            575: {
              slidesPerView: 1,
            },
            0: {
              slidesPerView: 2,
            }
          },
        });
      });

      $(document).ready(function () {
        var swiper = new Swiper(".mySwiper-banner-seven", {
          spaceBetween: 0,
          slidesPerView: 1,
          loop: true,
          speed: 2000,
          effect: 'fade',
          autoplay: {
            delay: 4000,
            disableOnInteraction: false,
          },
          navigation: {
            nextEl: ".swiper-button-next",
            prevEl: ".swiper-button-prev",
          },
        });
      });

      $(document).ready(function () {
        var swiper = new Swiper(".mySwiper-portfolio", {
          spaceBetween: 0,
          slidesPerView: 1,
          loop: true,
          speed: 1000,
          effect: 'fade',
          autoplay: {
            delay: 1500,
            disableOnInteraction: false,
          },
          navigation: {
            nextEl: ".swiper-button-next",
            prevEl: ".swiper-button-prev",
          },
        });
      });
      $(document).ready(function () {
        var swiper = new Swiper(".mySwiper-testimonials-2", {
          spaceBetween: 0,
          slidesPerView: 1,
          loop: true,
          speed: 500,
          // autoplay: {
          //   delay: 2000,
          // },
          pagination: {
            el: ".swiper-pagination",
            clickable: true
          },
        });
      });
    },

    wowActive: function () {
      new WOW().init();
    },

    stickyHeader: function (e) {
      $(window).scroll(function () {
        if ($(this).scrollTop() > 150) {
          $('.header--sticky').addClass('sticky')
        } else {
          $('.header--sticky').removeClass('sticky')
        }
      })
    },

    backToTopInit: function () {
      $(document).ready(function () {
        "use strict";

        var progressPath = document.querySelector('.progress-wrap path');
        var pathLength = progressPath.getTotalLength();
        progressPath.style.transition = progressPath.style.WebkitTransition = 'none';
        progressPath.style.strokeDasharray = pathLength + ' ' + pathLength;
        progressPath.style.strokeDashoffset = pathLength;
        progressPath.getBoundingClientRect();
        progressPath.style.transition = progressPath.style.WebkitTransition = 'stroke-dashoffset 10ms linear';
        var updateProgress = function () {
          var scroll = $(window).scrollTop();
          var height = $(document).height() - $(window).height();
          var progress = pathLength - (scroll * pathLength / height);
          progressPath.style.strokeDashoffset = progress;
        }
        updateProgress();
        $(window).scroll(updateProgress);
        var offset = 50;
        var duration = 550;
        jQuery(window).on('scroll', function () {
          if (jQuery(this).scrollTop() > offset) {
            jQuery('.progress-wrap').addClass('active-progress');
          } else {
            jQuery('.progress-wrap').removeClass('active-progress');
          }
        });
        jQuery('.progress-wrap').on('click', function (event) {
          event.preventDefault();
          jQuery('html, body').animate({ scrollTop: 0 }, duration);
          return false;
        })


      });
    },

    sideMenu: function () {

      // collups menu side right
      $(document).on('click', '#menu-btn', function () {
        $("#side-bar").addClass("show");
        $("#anywhere-home").addClass("bgshow");
      });
      $(document).on('click', '.close-icon-menu', function () {
        $("#side-bar").removeClass("show");
        $("#anywhere-home").removeClass("bgshow");
      });
      $(document).on('click', '#anywhere-home', function () {
        $("#side-bar").removeClass("show");
        $("#anywhere-home").removeClass("bgshow");
      });
      $(document).on('click', '.onepage .mainmenu li a', function () {
        $("#side-bar").removeClass("show");
        $("#anywhere-home").removeClass("bgshow");
      });
    },




    vedioActivation: function () {
      $(document).ready(function () {
        $('.popup-youtube, .popup-video').magnificPopup({
          type: 'iframe',
          mainClass: 'mfp-fade',
          removalDelay: 160,
          preloader: false,
          fixedContentPos: false
        });
      });
    },

    menuCurrentLink: function () {
      var currentPage = location.pathname.split("https://html.themewant.com/"),
        current = currentPage[currentPage.length - 1];
      $('.parent-nav li > a').each(function () {
        var $this = $(this);
        if ($this.attr('href') === current) {
          $this.addClass('active');
          $this.parents('.has-dropdown').addClass('menu-item-open')
        }
      });
    },


    preloader: function () {
      window.addEventListener('load', function () {
        document.querySelector('body').classList.add("loaded")
      });
    },

    datePicker: function () {
      $(function () {
        $("#datepicker").datepicker({
          dateFormat: "dd-mm-yy"
          , duration: "fast"
        });
      });
    },


  }

  rtsJs.m();
})(jQuery, window)







