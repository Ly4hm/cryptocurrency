use std::net::{UdpSocket, SocketAddr};
use std::str;
use std::sync::Mutex;
use std::time::Duration;
use rand::{thread_rng, Rng};
use rand::distributions::Alphanumeric;

#[derive(Debug)]
struct Session {
    id: String,
    addr: SocketAddr,
}

fn generate_id() -> String {
    thread_rng().sample_iter(&Alphanumeric).take(4).map(char::from).collect()
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.len() != 3 {
        eprintln!("Usage: {} <mode> <address>", args[0]);
        eprintln!("mode: 'server' or 'client'");
        eprintln!("address: server address for client mode, local address for server mode");
        std::process::exit(1);
    }

    let mode = &args[1];
    let address = &args[2];

    match mode.as_str() {
        "server" => run_server(address),
        "client" => run_client(address),
        _ => {
            eprintln!("Invalid mode: {}", mode);
            std::process::exit(1);
        }
    }
}

fn run_server(address: &str) {
    let session_list: Mutex<Vec<Session>>  = Mutex::new(Vec::new());

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
                sessions.push(Session { id: id.to_string(), addr: src });
                println!("Added new session: {} with id {}", src, id);
            }
        }

        // 请求处理
        if data == "Get sessions" {
            let response: Vec<String> = sessions.iter().map(|s| format!("{}:{}", s.id, s.addr)).collect();
            let response = response.join(",");
            socket.send_to(response.as_bytes(), src).expect("Couldn't send data");
            println!("Sent sessions to {}", src);
        } else {
            let response = b"Ok";
            socket.send_to(response, src).expect("Couldn't send data");
            println!("Sent 'Ok' to {}", src);
        }
    }
}

fn run_client(server_address: &str) {
    let socket = UdpSocket::bind("0.0.0.0:0").expect("Couldn't bind to address");
    let server_addr: SocketAddr = server_address.parse().expect("Invalid server address");

    let id = generate_id();
    let msg = format!("Hello from client:{}", id);
    let msg = msg.as_bytes();
    let mut attempts = 0;
    let max_attempts = 10;

    // 指数退避重传
    while attempts < max_attempts {
        socket.send_to(msg, server_addr).expect("Couldn't send data");
        println!("Sent '{}' to {}", str::from_utf8(msg).unwrap(), server_addr);

        let mut buf = [0; 1024];
        socket.set_read_timeout(Some(Duration::from_secs(1 << attempts))).expect("Couldn't set read timeout");

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

    if attempts == max_attempts {
        println!("Failed to receive 'Ok' after {} attempts", max_attempts);
        return;
    }

    // 获取 sessions
    let msg = b"Get sessions";
    socket.send_to(msg, server_addr).expect("Couldn't send data");
    println!("Sent '{}' to {}", str::from_utf8(msg).unwrap(), server_addr);

    let mut buf = [0; 1024];
    let (amt, src) = socket.recv_from(&mut buf).expect("Didn't receive data");
    let data = str::from_utf8(&buf[..amt]).expect("Couldn't parse data");
    println!("Received sessions from {}: {}", src, data);
}
