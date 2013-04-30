var mozilla_cert_id = false; // mozilla sertifikaadi id
var sign_ongoing = false;

function is_ongoing() {
  //TODO: $("#status").html("Signeerimine käib, ära sega!");
  if (sign_ongoing) { return true; }
  return false;
}

function get_cert() {

  if ($.browser.msie) {
    function controlOK() {
      if (typeof(axplugin)=="undefined") return false;
      if (axplugin==null) return false;
      if (axplugin.readyState != 4 ) return false;
      if (axplugin.object==null) return false;
      return true;
    }

    if (!controlOK()) {
      $("#debug").html("ActiveX komponendid puudu!");
      return false;
    }

    cert = axplugin.getSigningCertificate();
    if (!cert) {
        $("#debug").html("Sertifikaati ei leitud! Kontrolli lugejat/kaarti");
        return false;
    }
    return cert;
  } /* if msie */

  if ($.browser.mac || ($.browser.win && ($.browser.firefox || $.browser.mozilla))) {
       if ($.browser.win) {
         // is the plugin installed?
         navigator.plugins.refresh();
         var mime = navigator.mimeTypes['application/x-idcard-plugin'];
         if (!(mime && mime.enabledPlugin)) {
  		$("#status").html("Sa pead paigaldama allkirjastamise plugina Firefoxi jaoks. <a href='javascript:install_mozilla_plugin()'>Vajuta siia paigaldamiseks.</a>");
                return false;
	 }

       }
       if ($.browser.mac && !has_mozilla_plugin()) {
         $("#status").html("Sa pead paigaldama ID-kaardi tarkvara Mac OS X jaoks. <a href='http://installer.id.ee/'>Vajuta siia paigaldamiseks.</a>");
         return false;
       }


    try {
      var certList = new idCardPluginHandler('est').getCertificates();
      if (certList.length > 1) {
        $("#debug").html("FIXME: show cert select box");
      } else {
        $("#debug").html("Cert found!");
      }
      mozilla_cert_id = certList[0].id;
      return certList[0].cert;

    } catch(ex) {
      $("#debug").html(ex.message);
      if (ex.isCancelled()) {
        alert(ex.message);
      } else {
        $("#debug").html(ex.message);
      }
      return false;
    }
  } /* if mac */
  if ($.browser.linux) {
      if (applet_stage == 1) {
        return applet_certificate;
      } else {
        return false;
      }
  } /* if linux */
}

function get_signature(hash) {
  $("#debug").html("Certificate sent, Hash received, starting signing");
  // call actual signing method
  if ($.browser.msie) {
    var signature = axplugin.getSignedHash(hash, axplugin.selectedCertNumber);
    if (!signature) {
      $("#debug").html("Katkestatud või vale PIN kood!");
    } else {
      $("#debug").html("Allkiri: " + signature);
      return signature;
    }
  } else if ($.browser.mac || ($.browser.win && ($.browser.firefox || $.browser.mozilla))) {
    try {
      var signature = new idCardPluginHandler('est').sign(mozilla_cert_id, hash);
      $("#debug").html("Allkiri antud.");
      return signature;
    } catch(ex) {
      $("#debug").html(ex.message);
      if (ex.isCancelled()) {
        $("#status").html("Allkirjastamine katkestati");
      } else {
        $("#debug").html(ex.message);
      }
      return false;
    }
  } else if ($.browser.linux) {
      //
      if (applet_stage == 2) {
        return applet_signature;
      } else {
        return false;
      }
  } /* if linux */
}

function set_error_status(msg) {
    $("#status").html("Viga! " + msg);
}

function is_err(what, data, txtstatus) {
  $("#debug").html(what + " returns: " + data.status + ' ' + txtstatus);
  switch (data.status) {
    case "OK":
      return false;
    case "PHONE_ABSENT":
      set_error_status("Telefon pole levis.");
      break;
    case "USER_CANCEL":
      set_error_status("Mobiil-ID allkirjastamine katkestatud.");
      break;
    case "SENDING_ERROR":
      set_error_status("Saatmisviga (mobiil-ID teenus ei vasta).");
      break;
    case "INVALID_TOKEN":
      set_error_status("Vale mobiilinumber.");
      break;
    case "INTERNAL_ERROR":
      set_error_status("Sisemine viga.");
      break;
    case "POLL_COUNT_EXCEEDED":
      set_error_status("Mobiil-ID teenus ei vasta.");
      break;
    case "301":
      set_error_status("Sellel numbril pole mobiil-ID lepingut.");
      break;
    case "200":
      set_error_status("DigiDoc notariteenuse viga.");
      break;
    case "POST_FAILED":
      set_error_status("Brauser saatis puudulikud andmed. Palun proovi uuesti.");
      break;
    default:
      if (data.status.match("SIGNATURE_ERROR")) {
        set_error_status("Allkirja viga. Palun taaskäivita brauser ning allkirjasta uuesti.");
      } else {
        set_error_status("Tundmatu viga.");
      }
      break;
  }
  sign_ongoing = false;
  return true;
}

function sign_done_callback(data, txtstatus) {
   if (is_err("mid_finalize", data, txtstatus)) { return; }
   $("#status").html("Allkirjastamine õnnestus");
   sign_ongoing = false;
   sign_done();
}

function send_signature(signature) {
    $("#debug").html("send signature");
    $.post('/vote/id_finalize/', {'signature': signature}, sign_done_callback, 'json');
}


function sign_hash_callback(data, txtstatus) {
  if (is_err("id_prepare", data, txtstatus)) { return; }
  // TODO: $("#status").html("Etapp X sooritatud");

  // Callback called but user has not signed it yet.
  if ($.browser.linux && applet_stage < 2) {
    update_applet_code(data.hash);
    return;
  }

  var signature = get_signature(data.hash);
  if (signature) {
	send_signature(signature);
  } else {
    $("#debug").html("signing failed");
    // TODO: $("#status").html("Allkirjastamine nurjus");
    sign_ongoing = false;
    return;
  }
}

function idcard_sign() {
  // TODO: strings, i18n
  if (is_ongoing()) { return; }
  sign_ongoing = true;

  if ($.browser.linux && applet_stage < 1) return false; // Page just loaded

  $("#status").html("Allkirjastamine käivitub, palun oota.");

  // Post the certificate to the service, starting signing process
  var cert = get_cert();
  if (!cert) {
    // TODO: $("#status").html("Sertifikaati ei leitud");
    $("#status").html("Sertifikaati ei leitud. Kontrolli, et tarkvara oleks installeeritud, kaardilugeja ühendatud ning ID-kaart lugejas.");
    sign_ongoing = false;
    return;
  } else {
    function prepare_callback(data, txtstatus) {
      if (is_err("id_start", data, txtstatus)) { return; }
      // TODO: $("#status").html("Etapp X sooritatud");
      $.post('/vote/id_prepare/', {'certificate': cert}, sign_hash_callback, 'json');
    }

    $.post('/vote/id_start/', {}, prepare_callback, 'json');
  }
}

function is_digit(token) {
  var valid_chars = "0123456789";
  var i = 0;
  if (token.textAt(0) == '+') { i = 1; }
  for (; i < token.length; i++) {
    if (valid_chars.indexOf(token.textAt(i)) == -1) { return false; }
  }
  return true;
}

function mid_sign() {
  // TODO: strings, i18n

  if (is_ongoing()) { return; }
  sign_ongoing = true;

  $("#status").html("Allkirjastamine käivitub, palun oota.");


  var token = $("input#token").val();
  if (!token || token.length < 5 || token.length > 12) {
    // FIXME: is_digit(token)
    alert("Sisesta telefoninumber (5xxxxx)!"); // FIXME: või id-kood
    $("#status").html("Sisesta telefoninumber kujul 5xxxxx!");
    sign_ongoing = false;
    return false;
  }

  function mid_start_callback(data, txtstatus) {

    function mid_challenge_callback(data, txtstatus) {

      function mid_done_callback(data, txtstatus) {

        if (is_err("mid_finalize", data, txtstatus)) { return; }
        $("#status").html("Allkirjastamine õnnestus");
        sign_ongoing = false;
        sign_done();
      }

      if (is_err("mid_prepare", data, txtstatus)) { return; }
      $("#status").html("Kontrollkood: " + data.challenge);

      $.post('/vote/mid_finalize/', {}, mid_done_callback, 'json');
    }

    if (is_err("mid_start", data, txtstatus)) { return; }
    $("#debug").html("Mobiil ID esimene etapp õnnestus."); // TODO: fix string

    $.post('/vote/mid_prepare/', {'token': token}, mid_challenge_callback, 'json');
  }
  $.post('/vote/mid_start/', {}, mid_start_callback, 'json');
}

