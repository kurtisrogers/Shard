/**
 * Shard framework glue for HTMX + Alpine.js
 */
(function () {
  "use strict";

  document.addEventListener("DOMContentLoaded", function () {
    document.body.addEventListener("htmx:configRequest", function (event) {
      var detail = event.detail;
      if (!detail.parameters) {
        detail.parameters = {};
      }
      detail.parameters["shard"] = "1";
    });
  });

  document.addEventListener("alpine:init", function () {
  });

  document.addEventListener("shard:action-complete", function () {
  });
})();
