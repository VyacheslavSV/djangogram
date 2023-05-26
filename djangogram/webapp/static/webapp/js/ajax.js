/*
 * ATTENTION: The "eval" devtool has been used (maybe by default in mode: "development").
 * This devtool is neither made for production nor for readable output files.
 * It uses "eval()" calls to create a separate source file in the browser devtools.
 * If you are trying to read the output file, select a different devtool (https://webpack.js.org/configuration/devtool/)
 * or disable the default devtool with "devtool: false".
 * If you are looking for production-ready output files, see mode: "production" (https://webpack.js.org/configuration/mode/).
 */
/******/ (function() { // webpackBootstrap
/******/ 	var __webpack_modules__ = ({

/***/ "./src/js/ajax.js":
/*!************************!*\
  !*** ./src/js/ajax.js ***!
  \************************/
/***/ (function() {

eval("$(document).ready(function () {\n  $('.like-ajax').click(function (event) {\n    event.preventDefault();\n    var form = $(this).closest('form');\n    var url = form.attr('action');\n    $.ajax({\n      type: 'POST',\n      url: url,\n      data: form.serialize(),\n      dataTypes: \"json\",\n      context: this,\n      success: function (response) {\n        if (response.is_liked) {\n          $(this).text('Unlike');\n        } else {\n          $(this).text('Like');\n        }\n        $(this).toggleClass('btn-danger');\n        $(this).toggleClass('btn-success');\n        $(this).next(\".count_likes\").text(response.likes_count);\n      },\n      error: function (xhr, textStatus, errorThrown) {\n        console.log(xhr.status + ': ' + xhr.statusText);\n      }\n    });\n  });\n});\n$('.subscribe-ajax').click(function (event) {\n  event.preventDefault();\n  var form = $(this).closest('form');\n  var url = form.attr('action');\n  $.ajax({\n    type: 'POST',\n    url: url,\n    data: form.serialize(),\n    dataType: 'json',\n    context: this,\n    success: function (response) {\n      if (response.is_subscribed) {\n        $(this).text('Unsubscribed');\n      } else {\n        $(this).text('Subscribed');\n      }\n      $(this).toggleClass('btn-primary');\n      $(this).toggleClass('btn-secondary');\n    },\n    error: function (xhr, textStatus, errorThrown) {\n      console.log(xhr.status + ': ' + xhr.statusText);\n    }\n  });\n});\n\n//# sourceURL=webpack://frontend/./src/js/ajax.js?");

/***/ })

/******/ 	});
/************************************************************************/
/******/ 	
/******/ 	// startup
/******/ 	// Load entry module and return exports
/******/ 	// This entry module can't be inlined because the eval devtool is used.
/******/ 	var __webpack_exports__ = {};
/******/ 	__webpack_modules__["./src/js/ajax.js"]();
/******/ 	
/******/ })()
;