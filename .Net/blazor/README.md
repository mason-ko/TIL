## Div Class 조건 걸기

```html
<div class="received_withd_msg@((contents.UserId== this._tokenInfo.UserId ? "_mine" : ""))">
```

위 처럼 @() 로 삼항연산자 가능

## SignalR 사용 허브 연결


Startup.cs
```c#
 app.UseEndpoints(endpoints =>
            {
                endpoints.MapBlazorHub();
                endpoints.MapHub<ChatHub>("/chathub");
            });
```

ChatHub.cs
```c#
public class ChatHub : Hub
    {
        public async Task SendMessage(string user, string message)
        {
            await Clients.All.SendAsync("ReceiveMessage", user, message);
        }
    }
```

.razor file cs code
```c#    
 private async void InitHubClient()
  {
    _hubConnection = new HubConnectionBuilder()
      .WithUrl(NavManager.ToAbsoluteUri("/chathub"))
      .Build();

    _hubConnection.On<string, string>("ReceiveMessage", (t, message) =>
    {
      var encodedMsg = $"{t}: {message}";
      Console.WriteLine(encodedMsg);
      StateHasChanged();
    });

    await _hubConnection.StartAsync();
  }
```
보낼땐
```c#
await _hubConnection.SendAsync("SendMessage", "ABCD", JsonConvert.SerializeObject(contents));
```

+ _hubConnection 에서 ReceiveMessage 받을 때 보내는 유형의 class가 각각 다를 경우 json string 으로 보내 처리하는게 편한듯
