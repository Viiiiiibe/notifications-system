(function(){
  function buildSocketUrl() {
    var loc = window.location;
    var wsStart = loc.protocol === 'https:' ? 'wss://' : 'ws://';
    return wsStart + loc.host + '/ws/admin/notifications/';
  }

  try {
    var socket = new WebSocket(buildSocketUrl());

    socket.addEventListener('open', function() {
      console.log('Admin notifications websocket connected');
    });

    socket.addEventListener('message', function(e) {
      try {
        var data = JSON.parse(e.data);
      } catch(err) {
        console.warn('Invalid notification payload', e.data);
        return;
      }
      showToast(data.title || 'Notification', data.text || '');
    });

    socket.addEventListener('close', function() {
      console.log('Admin notifications websocket closed');
    });
  } catch (err) {
    console.warn('WebSocket not available:', err);
  }

  function showToast(title, text) {
    var container = document.getElementById('admin-notifications-container');
    if(!container) {
      container = document.createElement('div');
      container.id = 'admin-notifications-container';
      container.style.position = 'fixed';
      container.style.top = '16px';
      container.style.right = '16px';
      container.style.zIndex = 9999;
      document.body.appendChild(container);
    }
    var toast = document.createElement('div');
    toast.className = 'admin-notif-toast';
    toast.setAttribute('role', 'status');
    toast.setAttribute('aria-live', 'polite');

    var h = document.createElement('strong');
    h.innerText = title;
    var p = document.createElement('div');
    p.innerText = text;
    toast.appendChild(h);
    toast.appendChild(p);
    container.appendChild(toast);

    setTimeout(function(){
      toast.style.transition = 'opacity 0.5s, transform 0.5s';
      toast.style.opacity = 0;
      toast.style.transform = 'translateY(-8px)';
      setTimeout(function(){ if (toast.parentElement) toast.parentElement.removeChild(toast); }, 500);
    }, 6000);
  }
})();