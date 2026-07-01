(function () {
  "use strict";

  document.addEventListener("DOMContentLoaded", function () {
    document.body.addEventListener("htmx:configRequest", function (event) {
      var detail = event.detail;
      if (!detail.parameters) {
        detail.parameters = {};
      }
      detail.parameters.shard = "1";
    });
  });
})();
