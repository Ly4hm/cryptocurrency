use rand::distributions::Alphanumeric;
use rand::{thread_rng, Rng};
use std::io::{self, Write};
use std::net::{SocketAddr, UdpSocket};
use std::str;
use std::sync::Mutex;
use std::time::Duration;

#[derive(Debug)]
struct Session {
    id: String,
    addr: SocketAddr,
}

fn generate_id() -> String {
    thread_rng()
        .sample_iter(&Alphanumeric)
        .take(4)
        .map(char::from)
        .collect()
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.len() < 3 || args.len() > 4 {
        eprintln!("Usage: {} <mode> <address> [-l]", args[0]);
        eprintln!("mode: 'server' or 'client'");
        eprintln!("address: server address for client mode, local address for server mode");
        eprintln!("optional: -l to listen for incoming messages after hello");
        std::process::exit(1);
    }

    let mode = &args[1];
    let address = &args[2];
    let listen = args.len() == 4 && args[3] == "-l";

    match mode.as_str() {
        "server" => run_server(address),
        "client" => run_client(address, listen),
        _ => {
            eprintln!("Invalid mode: {}", mode);
            std::process::exit(1);
        }
    }
}

fn run_server(address: &str) {
    let session_list: Mutex<Vec<Session>> = Mutex::new(Vec::new());

    let socket = UdpSocket::bind(address).expect("Couldn't bind to address");
    println!("Server listening on {}", address);

    let mut buf = [0; 1024];
    // 循环监听客户端请求
    loop {
        let (amt, src) = socket.recv_from(&mut buf).expect("Didn't receive data");
        let data = str::from_utf8(&buf[..amt]).expect("Couldn't parse data");
        println!("Received '{}' from {}", data, src);

        let mut sessions = session_list.lock().unwrap();
        if data.starts_with("Hello from client:") {
            let id = &data["Hello from client:".len()..];
            if let Some(session) = sessions.iter_mut().find(|s| s.id == id) {
                session.addr = src;
                println!("Updated session: {} with new address {}", id, src);
            } else {
                sessions.push(Session {
                    id: id.to_string(),
                    addr: src,
                });
                println!("Added new session: {} with id {}", src, id);
            }
        }

        if data.starts_with("Get address:") {
            let id = &data["Get address:".len()..];
            if let Some(session) = sessions.iter().find(|s| s.id == id) {
                let response = format!("{}:{}", session.id, session.addr);
                socket
                    .send_to(response.as_bytes(), src)
                    .expect("Couldn't send data");
                println!("Sent address of {} to {}", id, src);
            } else {
                let response = b"Not found";
                socket.send_to(response, src).expect("Couldn't send data");
                println!("Sent 'Not found' to {}", src);
            }
        } else if data == "Get sessions" {
            let response: Vec<String> = sessions
                .iter()
                .map(|s| format!("{}:{}", s.id, s.addr))
                .collect();
            let response = response.join(",");
            socket
                .send_to(response.as_bytes(), src)
                .expect("Couldn't send data");
            println!("Sent sessions to {}", src);
        } else {
            let response = b"Ok";
            socket.send_to(response, src).expect("Couldn't send data");
            println!("Sent 'Ok' to {}", src);
        }
    }
}

fn run_client(server_address: &str, listen: bool) {
    let socket = UdpSocket::bind("0.0.0.0:0").expect("Couldn't bind to address");
    let server_addr: SocketAddr = server_address.parse().expect("Invalid server address");

    let id = generate_id();
    let msg = format!("Hello from client:{}", id);
    let msg = msg.as_bytes();
    let mut attempts = 0;
    let max_attempts = 10;

    // 指数退避重传
    while attempts < max_attempts {
        socket
            .send_to(msg, server_addr)
            .expect("Couldn't send data");
        println!("Sent '{}' to {}", str::from_utf8(msg).unwrap(), server_addr);

        let mut buf = [0; 1024];
        socket
            .set_read_timeout(Some(Duration::from_secs(1 << attempts)))
            .expect("Couldn't set read timeout");

        match socket.recv_from(&mut buf) {
            Ok((amt, src)) => {
                let data = str::from_utf8(&buf[..amt]).expect("Couldn't parse data");
                if data == "Ok" {
                    println!("Received '{}' from {}", data, src);
                    break;
                }
            }
            Err(e) => {
                println!("Attempt {} failed: {}", attempts + 1, e);
            }
        }

        attempts += 1;
    }

    // 重传次数达到上限
    if attempts == max_attempts {
        println!("Failed to receive 'Ok' after {} attempts", max_attempts);
        return;
    }

    if listen {
        // 持续接收传回来的消息
        socket
            .set_read_timeout(Some(Duration::from_secs(60)))
            .expect("Couldn't set read timeout");
        loop {
            let mut buf = [0; 1024];
            match socket.recv_from(&mut buf) {
                Ok((amt, src)) => {
                    let data = str::from_utf8(&buf[..amt]).expect("Couldn't parse data");
                    println!("Received '{}' from {}", data, src);
                    let response = b"Message received";
                    socket.send_to(response, src).expect("Couldn't send data");
                    println!("Sent 'Message received' to {}", src);
                }
                Err(e) => {
                    println!("Receive failed: {}", e);
                    break;
                }
            }
        }
    } else {
        // 获取 sessions
        let msg = b"Get sessions";
        socket
            .send_to(msg, server_addr)
            .expect("Couldn't send data");
        println!("Sent '{}' to {}", str::from_utf8(msg).unwrap(), server_addr);

        let mut buf = [0; 1024];
        let (amt, _src) = socket.recv_from(&mut buf).expect("Didn't receive data");
        let data = str::from_utf8(&buf[..amt]).expect("Couldn't parse data");
        // println!("Received sessions from {}: {}", src, data);

        // 解析 sessions
        let sessions: Vec<&str> = data.split(',').collect();
        for (i, session) in sessions.iter().enumerate() {
            println!("  > {}: {}", i, session);
        }

        // 选择目标客户端
        print!("Enter the number of the client you want to communicate with: ");
        io::stdout().flush().unwrap();
        let mut input = String::new();
        io::stdin()
            .read_line(&mut input)
            .expect("Failed to read line");
        let index: usize = input.trim().parse().expect("Invalid number");

        if index >= sessions.len() {
            println!("Invalid selection");
            return;
        }

        // 获取目标客户端地址
        let target_session = sessions[index];
        let parts = target_session.split(':').collect::<Vec<&str>>();
        let target_addr: SocketAddr = format!("{}:{}", parts[1], parts[2])
            .parse()
            .expect("Invalid address");
        let target_id = target_session.split(':').next().unwrap();
        let msg = format!("[Data] Hello to <{}>", target_id);
        socket
            .send_to(msg.as_bytes(), target_addr)
            .expect("Couldn't send data");
        println!("Sent '{}' to {}", msg, target_addr);

        // 持续接收传回来的消息,超时时间为60s
        socket
            .set_read_timeout(Some(Duration::from_secs(60)))
            .expect("Couldn't set read timeout");
        loop {
            let mut buf = [0; 1024];
            match socket.recv_from(&mut buf) {
                Ok((amt, src)) => {
                    let data = str::from_utf8(&buf[..amt]).expect("Couldn't parse data");
                    println!("Received '{}' from {}", data, src);
                }
                Err(e) => {
                    println!("Receive failed: {}", e);
                    break;
                }
            }
        }
    }
}
