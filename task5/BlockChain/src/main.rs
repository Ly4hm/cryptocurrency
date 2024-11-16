#![allow(unused)]

extern crate sha2;

use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::{
    rc::Rc,
    time::{SystemTime, UNIX_EPOCH},
};

const DIFICULTY: u32 = 4;

fn main() {}

/// 区块
#[derive(Debug)]
struct Block {
    transactions: Rc<Vec<Transaction>>,
    privios_hash: String,
    nouce: u64,
    timestamp: u64,
    current_hash: String,
}

impl Block {
    fn new(transaction: Rc<Vec<Transaction>>, privios_hash: String) -> Block {
        let mut new_block = Block {
            transactions: transaction,
            privios_hash,
            nouce: 1,
            timestamp: SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_secs(),
            current_hash: String::new(),
        };
        new_block.current_hash = new_block.calculate_hash();

        new_block
    }

    /// 计算区块的hash
    fn calculate_hash(&self) -> String {
        let mut hasher = Sha256::new();
        hasher.update(
            serde_json::to_string(&*self.transactions)
                .unwrap()
                .as_bytes(),
        );
        hasher.update(self.privios_hash.as_bytes());
        hasher.update(self.nouce.to_string().as_bytes());
        hasher.update(self.timestamp.to_string().as_bytes());
        let result = hasher.finalize();
        format!("{:x}", result)
    }

    /// 挖矿
    fn mine(&mut self, dificulty: u32) -> String {
        let mut hash = self.calculate_hash();
        while !hash.starts_with(&"0".repeat(dificulty as usize)) {
            self.nouce += 1;
            hash = self.calculate_hash();
        }
        println!("挖矿结束 hash: {}", hash);
        hash
    }
}

/// 区块链
#[derive(Debug)]
struct Chain {
    chain: Vec<Block>,
    dificulty: u32,
    transaction_pool: Rc<Vec<Transaction>>,
    mining_reward: f64,
}

impl Chain {
    fn new() -> Chain {
        Chain {
            chain: vec![Block::new(
                Rc::new(vec![]),
                String::from("Genesis_block is here!!!"),
            )], // 放入创世区块
            dificulty: DIFICULTY,
            transaction_pool: Rc::new(vec![]),
            mining_reward: 100.0,
        }
    }

    /// 设置难度
    fn set_difficulty(&mut self, dificulty: u32) {
        self.dificulty = dificulty;
    }

    /// 添加区块
    fn add_block(&mut self, mut new_block: Block) {
        new_block.current_hash = new_block.mine(self.dificulty);

        self.chain.push(new_block);
    }

    /// 挖矿并添加到区块链
    fn mine_transaction_pool(&mut self, miner_address: String) {
        // 发放矿工奖励
        let mine_transaction = Transaction::new(
            String::from("BlockChain_System"), // 第一笔由区块链发放
            miner_address,
            self.mining_reward,
        );
        Rc::get_mut(&mut self.transaction_pool)
            .unwrap()
            .push(mine_transaction);

        // 挖矿
        let rc_transaction_pool = Rc::clone(&self.transaction_pool);
        let mut new_block = Block::new(rc_transaction_pool, self.last_hash());

        // 添加到区块链
        // 清空 transaction_pool
        self.chain.push(new_block);
        Rc::get_mut(&mut self.transaction_pool).unwrap().clear();
    }

    /// 获取最后一个区块
    fn last_block(&self) -> &Block {
        self.chain.last().unwrap()
    }

    /// 获取最后一个区块的hash
    fn last_hash(&self) -> String {
        self.last_block().current_hash.clone()
    }

    /// 验证区块链
    fn validate(&self) -> bool {
        for i in 1..self.chain.len() {
            let current_block = &self.chain[i];
            let privios_block = &self.chain[i - 1];
            let calculate_hash = current_block.calculate_hash();
            if current_block.current_hash != calculate_hash {
                return false;
            }
            if current_block.privios_hash != privios_block.current_hash {
                return false;
            }
        }
        true
    }
}

/// 测试 - 保证区块链正确性
#[test]
fn test_chain() {
    // 创建一个新的区块链
    let mut blockchain = Chain::new();
}

/// 交易数据
#[derive(Debug, Serialize, Deserialize)]
struct Transaction {
    from: String,
    to: String,
    amount: f64, // 金额
}

impl Transaction {
    fn new(from: String, to: String, amount: f64) -> Transaction {
        Transaction { from, to, amount }
    }
}
