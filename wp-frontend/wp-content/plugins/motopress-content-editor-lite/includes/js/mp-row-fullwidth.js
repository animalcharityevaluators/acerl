(function(a){a(function(){function b(){var b=a(".mp-row-fluid.mp-row-fullwidth, .mp-row-fluid.mp-row-fullwidth-content");a.each(b,function(){var c=a(this);c.css({width:"","padding-left":"","margin-left":"","padding-right":"","margin-right":""});var b=c.hasClass("mp-row-fullwidth-content"),d=c.offset().left,e=a("html").width()-d-a(c).width(),f=b?"":d-parseInt(a(c).css("border-left-width"))+parseInt(a(c).css("padding-left")),b=b?"":e-parseInt(a(c).css("border-right-width"))-parseInt(a(c).css("padding-right")),
g=a("html").width();a(c).css({width:g,"padding-left":f,"margin-left":-d,"padding-right":b,"margin-right":-e})});a(window).trigger("mpce-row-size-update")}b();if(parent.hasOwnProperty("MP")&&parent.MP.hasOwnProperty("Editor"))parent.MP.Editor.onIfr("Resize",function(){b()});var d;a(window).resize(function(){d&&clearTimeout(d);d=setTimeout(function(){b()},500)})})})(jQuery);
